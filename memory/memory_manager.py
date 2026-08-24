"""
==================================================
REETA — memory/memory_manager.py
==================================================
PURPOSE:
    The central coordinator for REETA's Phase 2 Memory System.
    Connects the classifier, embedder, vector store, and SQLite DB.
==================================================
"""

import threading
from typing import List
from utils.logger import get_logger

from database.db import get_db, init_db
from database.schemas import MemoryRecord, UserProfile, ConversationHistory
from memory.memory_models import MemoryEntry
from memory.embeddings import Embedder
from memory.vector_store import VectorStore
from memory.memory_classifier import MemoryClassifier
from memory.retrieval_engine import RetrievalEngine

logger = get_logger(__name__)

class MemoryManager:
    """
    Orchestrates the entire memory lifecycle.
    """
    
    def __init__(self, brain):
        logger.info("Initializing Phase 2 Memory System...")
        
        # 1. Initialize SQLite Database
        init_db()
        
        # 2. Initialize Components
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.classifier = MemoryClassifier(brain)
        self.retrieval_engine = RetrievalEngine(self.embedder, self.vector_store)
        
        logger.info("Memory System Initialized ✓")

    def process_interaction_async(self, user_input: str):
        """
        Processes a user interaction in a separate thread so it doesn't 
        block REETA's quick verbal responses.
        """
        if not user_input:
            return
            
        thread = threading.Thread(target=self._process_interaction, args=(user_input,))
        thread.daemon = True
        thread.start()

    def _process_interaction(self, user_input: str):
        """
        The actual memory pipeline:
        1. Classify input
        2. Embed if it's worth remembering
        3. Save to Vector Store (Chroma)
        4. Save to Database (SQLite)
        """
        try:
            # 1. Classify
            classification = self.classifier.classify(user_input)
            
            if not classification.should_remember or not classification.extracted_fact:
                return  # Nothing to remember
                
            # 1.5. Deduplication check
            # Check if this exact or highly similar fact already exists
            existing_context = self.retrieval_engine.retrieve_context(classification.extracted_fact)
            
            # Simple text matching (or could use Levenshtein distance)
            if any(classification.extracted_fact.lower() in existing.lower() for existing in existing_context):
                logger.info(f"Memory deduplication: '{classification.extracted_fact}' is already known. Skipping.")
                return

            # Create the MemoryEntry model
            memory = MemoryEntry(
                content=classification.extracted_fact,
                category=classification.category,
                metadata={"source": "conversation"}
            )
            
            # 2. Embed
            embedding = self.embedder.embed_text(memory.content)
            if not embedding:
                logger.error("Failed to generate embedding. Aborting memory save.")
                return
                
            # 3. Save to Vector Store
            success = self.vector_store.add_memory(memory, embedding)
            if not success:
                return
                
            # 4. Save to Database (Source of Truth)
            self._save_to_db(memory)
            
        except Exception as e:
            logger.error(f"Error in memory pipeline: {e}", exc_info=True)

    def _save_to_db(self, memory: MemoryEntry):
        """Saves the memory to SQLite using SQLAlchemy."""
        try:
            # get_db is a generator, so we use next() to get the session
            db_gen = get_db()
            db = next(db_gen)
            
            record = MemoryRecord(
                vector_id=memory.id,
                content=memory.content,
                category=memory.category,
                metadata_json=memory.metadata
            )
            
            db.add(record)
            db.commit()
            logger.debug(f"Memory {memory.id} saved to SQLite")
            
        except StopIteration:
            logger.error("Failed to get DB session")
        except Exception as e:
            logger.error(f"Failed to save memory to SQLite: {e}")

    def get_relevant_context(self, user_input: str) -> List[str]:
        """
        Retrieves context relevant to the user's input.
        Called by the Brain BEFORE responding.
        """
        return self.retrieval_engine.retrieve_context(user_input)

    # --- Phase 2 Extensions: Conversations and User Profile ---

    def log_conversation(self, role: str, content: str):
        """Logs a single turn of the conversation to SQLite."""
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            record = ConversationHistory(role=role, content=content)
            db.add(record)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log conversation to DB: {e}")

    def get_recent_conversation(self, limit: int = 10) -> List[dict]:
        """Retrieves the most recent conversation history from SQLite."""
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            records = db.query(ConversationHistory).order_by(ConversationHistory.created_at.desc()).limit(limit).all()
            # Return in chronological order
            return [{"role": r.role, "content": r.content} for r in reversed(records)]
        except Exception as e:
            logger.error(f"Failed to retrieve conversation from DB: {e}")
            return []

    def set_user_profile(self, key: str, value: str):
        """Sets a key-value pair in the user profile."""
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            record = db.query(UserProfile).filter_by(key=key).first()
            if record:
                record.value = value
            else:
                record = UserProfile(key=key, value=value)
                db.add(record)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to set user profile: {e}")

    def get_user_profile(self) -> dict:
        """Retrieves the entire user profile as a dictionary."""
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            records = db.query(UserProfile).all()
            return {r.key: r.value for r in records}
        except Exception as e:
            logger.error(f"Failed to retrieve user profile: {e}")
            return {}

    # --- Memory Management CLI Interface ---

    def list_memories(self) -> List[dict]:
        """Returns all saved facts from the database."""
        try:
            db_gen = get_db()
            db = next(db_gen)
            records = db.query(MemoryRecord).all()
            return [{"id": r.id, "content": r.content, "category": r.category} for r in records]
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            return []

    def delete_memory(self, memory_id: int) -> bool:
        """Deletes a memory by its SQLite ID."""
        try:
            db_gen = get_db()
            db = next(db_gen)
            record = db.query(MemoryRecord).filter_by(id=memory_id).first()
            if record:
                # Need to delete from ChromaDB as well
                self.vector_store.collection.delete(ids=[record.vector_id])
                db.delete(record)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False

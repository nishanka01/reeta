"""
==================================================
REETA — memory/vector_store.py
==================================================
PURPOSE:
    Wraps the ChromaDB local vector database.
    Responsible for adding, retrieving, and deleting 
    memory vectors and metadata.
==================================================
"""

import os
from typing import List, Dict, Any, Optional
from config.settings import settings
from utils.logger import get_logger
from memory.memory_models import MemoryEntry

logger = get_logger(__name__)

class VectorStore:
    """
    Manages the ChromaDB instance for semantic search.
    Stores data locally in the 'data/chromadb' directory.
    """
    
    def __init__(self):
        # We ensure ChromaDB stores its data persistently on disk
        self.persist_directory = os.path.join(settings.BASE_DIR, "data", "chromadb")
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.collection_name = "reeta_memories"
        self.client = None
        self.collection = None
        
        self._init_chroma()

    def _init_chroma(self):
        """Initializes the ChromaDB client and collection."""
        try:
            import chromadb
            # Initialize persistent client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create the collection
            # We don't use Chroma's built-in embedding function here, 
            # because we generate embeddings explicitly in Embedder to have more control.
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"} # Cosine similarity works best for text embeddings
            )
            
            count = self.collection.count()
            logger.info(f"Vector store initialized at {self.persist_directory} ({count} memories)")
            
        except ImportError:
            logger.error("chromadb not installed. Run: pip install chromadb")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}", exc_info=True)

    def add_memory(self, memory: MemoryEntry, embedding: List[float]) -> bool:
        """
        Adds a memory entry and its semantic vector to ChromaDB.
        """
        if not self.collection:
            logger.warning("ChromaDB not initialized. Cannot add memory.")
            return False
            
        if not embedding:
            logger.warning("Empty embedding provided. Cannot add memory.")
            return False

        try:
            # Combine core attributes and custom metadata into the Chroma metadata dict
            meta = {
                "category": memory.category,
                "created_at": memory.created_at.isoformat()
            }
            meta.update(memory.metadata)
            
            self.collection.add(
                ids=[memory.id],
                embeddings=[embedding],
                documents=[memory.content],
                metadatas=[meta]
            )
            logger.info(f"Added memory {memory.id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add memory to vector store: {e}")
            return False

    def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches for memories semantically similar to the query embedding.
        
        Args:
            query_embedding: The vector of the user's current query
            limit: Maximum number of memories to return
            category_filter: Optional category to restrict search (e.g., "preference")
            
        Returns:
            A list of dictionaries containing retrieved documents, metadata, and distances.
        """
        if not self.collection or not query_embedding:
            return []

        try:
            where_clause = None
            if category_filter:
                where_clause = {"category": category_filter}

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Chroma returns lists of lists (one for each query). 
            # We only have one query, so we take index 0.
            retrieved = []
            
            if results and results["ids"] and len(results["ids"][0]) > 0:
                ids = results["ids"][0]
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                distances = results["distances"][0]
                
                for i in range(len(ids)):
                    retrieved.append({
                        "id": ids[i],
                        "document": docs[i],
                        "metadata": metas[i],
                        "distance": distances[i] # In Cosine space, lower distance = more similar
                    })
            
            return retrieved
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

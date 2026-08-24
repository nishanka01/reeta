"""
==================================================
REETA — memory/retrieval_engine.py
==================================================
PURPOSE:
    Retrieves semantically relevant memories based on the 
    user's current input.
==================================================
"""

from typing import List
from utils.logger import get_logger
from config.settings import settings
from memory.embeddings import Embedder
from memory.vector_store import VectorStore

logger = get_logger(__name__)

class RetrievalEngine:
    """
    Coordinates the embedding of a query and searching the vector store.
    """
    
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store
        
        # A threshold for distance. In cosine similarity, lower is better.
        # This prevents injecting completely unrelated memories just because they 
        # were the "closest" available.
        self.distance_threshold = 1.2

    def retrieve_context(self, user_input: str) -> List[str]:
        """
        Finds relevant memories for the current query.
        
        Returns:
            A list of string facts to inject into the LLM prompt.
        """
        if not user_input:
            return []
            
        logger.info(f"Retrieving context for query: '{user_input[:40]}...'")
        
        # 1. Embed the user's query
        query_vector = self.embedder.embed_text(user_input)
        if not query_vector:
            return []
            
        # 2. Search the vector store with limits from settings
        results = self.vector_store.search_similar(
            query_vector, limit=settings.MEMORY_MAX_CONTEXT_ITEMS
        )
        
        # 3. Filter by threshold and extract the facts
        relevant_facts = []
        for res in results:
            dist = res.get("distance", 999.0)
            doc = res.get("document", "")
            
            if dist <= self.distance_threshold and doc:
                relevant_facts.append(doc)
                logger.debug(f"Retrieved memory (dist={dist:.2f}): {doc}")
                
        if relevant_facts:
            logger.info(f"Found {len(relevant_facts)} relevant memories.")
            
        return relevant_facts

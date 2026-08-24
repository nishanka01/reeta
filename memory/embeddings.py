"""
==================================================
REETA — memory/embeddings.py
==================================================
PURPOSE:
    Provides functionality to convert text strings into 
    numerical vectors (embeddings) using the Google Gemini API.
    
    Embeddings capture the semantic meaning of text, allowing
    for searches based on concept rather than exact keywords.
==================================================
"""

from typing import List
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class Embedder:
    """
    Handles generating text embeddings.
    Uses Google Gemini's text-embedding-004 model for high-quality embeddings.
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-embedding-001"
        
        if not self.api_key:
            logger.error("No Gemini API key found for embeddings. Semantic search will fail.")
            self._client = None
        else:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Embedder initialized (Gemini)")
            except ImportError:
                logger.error("google-genai library not installed. Run: pip install google-genai")
                self._client = None

    def embed_text(self, text: str) -> List[float]:
        """
        Converts a single string of text into a vector.
        
        Args:
            text: The string to embed (e.g., "My favorite color is blue")
            
        Returns:
            A list of floats representing the semantic meaning.
        """
        if not self._client:
            logger.warning("Embedder has no client. Returning empty vector.")
            return []
            
        try:
            # We replace newlines to ensure better embedding quality
            clean_text = text.replace("\n", " ")
            
            response = self._client.models.embed_content(
                model=self.model,
                contents=clean_text,
            )
            
            return list(response.embeddings[0].values)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []

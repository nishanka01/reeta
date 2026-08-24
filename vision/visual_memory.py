"""
==================================================
REETA — vision/visual_memory.py
==================================================
PURPOSE:
    Handles indexing of OCR text and saving screenshots so
    they can be retrieved by the MemoryAgent later.
==================================================
"""

import os
from datetime import datetime
import json
from utils.logger import get_logger

logger = get_logger("vision.visual_memory")

class VisualMemory:
    def __init__(self):
        self.metadata_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "visual_metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    def store_ocr_context(self, image_path: str, extracted_text: str, context_tags: list = None):
        """
        Saves OCR metadata alongside an image path. 
        In the future, this will push to ChromaDB.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data = {
                "timestamp": timestamp,
                "image_path": image_path,
                "extracted_text": extracted_text,
                "tags": context_tags or []
            }
            
            filepath = os.path.join(self.metadata_dir, f"visual_meta_{timestamp}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                
            logger.info(f"Stored visual memory context for {image_path}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to store visual memory: {str(e)}")
            return None

# Singleton instance
visual_memory = VisualMemory()

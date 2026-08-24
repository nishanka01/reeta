"""
==================================================
REETA — multimodal/vision_context_manager.py
==================================================
PURPOSE:
    Takes raw visual data (OCR text, bounding boxes) and formats it
    into structured context for the LLM agents.
==================================================
"""

from utils.logger import get_logger

logger = get_logger("multimodal.context")

class VisionContextManager:
    def __init__(self):
        pass

    def format_screen_context(self, ocr_text: str, window_title: str = "Unknown") -> str:
        """
        Formats OCR and active window data into a prompt-friendly string.
        """
        if not ocr_text.strip():
            return f"[Active Window: {window_title}]\nNo readable text detected on screen."

        return (
            f"--- VISUAL CONTEXT ---\n"
            f"[Active Window: {window_title}]\n"
            f"Extracted Screen Text:\n"
            f"{ocr_text}\n"
            f"----------------------\n"
        )

    def format_ui_elements(self, bounding_boxes: list) -> str:
        """
        Converts bounding box dictionaries into readable UI layouts for the automation agent.
        """
        if not bounding_boxes:
            return "No UI elements detected."
            
        summary = "Detected UI Elements:\n"
        for i, box in enumerate(bounding_boxes):
            text = box.get('text', 'Icon')
            x, y = box.get('x'), box.get('y')
            summary += f"{i+1}. '{text}' at coordinates ({x}, {y})\n"
            
        return summary

# Singleton instance
vision_context = VisionContextManager()

import os
from utils.logger import get_logger

logger = get_logger(__name__)

class VisionManager:
    def __init__(self):
        self.has_tesseract = False
        try:
            import pytesseract
            from PIL import Image
            self.pytesseract = pytesseract
            self.Image = Image
            # Windows tesseract path usually needs to be set, assuming default or PATH
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self.has_tesseract = True
        except ImportError:
            logger.warning("pytesseract or Pillow not installed. OCR will not work.")

    def scan_document(self, file_path: str) -> str:
        """Scans a document image and extracts text."""
        if not self.has_tesseract:
            return "OCR is not available. Please install pytesseract and Pillow."
            
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
            
        try:
            logger.info(f"Scanning document: {file_path}")
            img = self.Image.open(file_path)
            text = self.pytesseract.image_to_string(img)
            
            if not text.strip():
                return "No text could be extracted from the image."
                
            return f"Extracted Text:\n{text[:500]}..." # Return truncated text for brevity
        except Exception as e:
            logger.error(f"Failed to scan document: {e}")
            return f"An error occurred while scanning the document."

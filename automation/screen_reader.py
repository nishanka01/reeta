"""
==================================================
REETA — automation/screen_reader.py
==================================================
PURPOSE:
    Provides screen awareness using PyTesseract OCR.
    Extracts text from screenshots to find UI elements.
==================================================
"""

from utils.logger import get_logger

try:
    from PIL import ImageGrab
    import pytesseract
    import cv2
    import numpy as np
    # Note: Tesseract-OCR must be installed on the system and in PATH
    # Default Windows installation path: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    pass

logger = get_logger(__name__)

class ScreenReader:
    """Uses OCR to understand the current screen."""

    def __init__(self):
        logger.info("ScreenReader initialized with OpenCV preprocessing.")

    def _preprocess_image(self, image) -> np.ndarray:
        """
        Converts the PIL Image to a cv2 numpy array, converts to grayscale,
        and applies binarization (thresholding) to improve OCR accuracy.
        """
        # Convert PIL to OpenCV format
        cv_img = np.array(image)
        # Convert RGB to BGR
        cv_img = cv_img[:, :, ::-1].copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # Apply Otsu's thresholding for binarization
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        return thresh

    def read_screen_text(self) -> str:
        """Takes a screenshot and extracts all text."""
        try:
            screenshot = ImageGrab.grab()
            processed_img = self._preprocess_image(screenshot)
            text = pytesseract.image_to_string(processed_img)
            logger.info("Successfully extracted text from screen.")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed. Is Tesseract installed? Error: {e}")
            return ""

    def find_text_coordinates(self, target_text: str) -> tuple[int, int] | None:
        """
        Finds the (x, y) coordinates of a specific word on the screen.
        Useful for clicking buttons that can't be found via standard UI automation.
        """
        try:
            screenshot = ImageGrab.grab()
            processed_img = self._preprocess_image(screenshot)
            
            data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
            
            target_lower = target_text.lower()
            
            for i, word in enumerate(data['text']):
                if target_lower in word.lower().strip():
                    # Return center coordinates of the bounding box
                    x = data['left'][i] + (data['width'][i] // 2)
                    y = data['top'][i] + (data['height'][i] // 2)
                    logger.info(f"Found '{target_text}' at ({x}, {y})")
                    return (x, y)
                    
            logger.warning(f"Could not find text '{target_text}' on screen.")
            return None
        except Exception as e:
            logger.error(f"Failed to locate text: {e}")
            return None

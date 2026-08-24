"""
==================================================
REETA — vision/ocr_engine.py
==================================================
PURPOSE:
    Extracts text from images using Tesseract OCR.
    Includes OpenCV preprocessing to improve read accuracy.
==================================================
"""

import cv2
import pytesseract
import numpy as np
from utils.logger import get_logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = get_logger("vision.ocr")

# Setup a dedicated thread pool for heavy vision tasks
vision_pool = ThreadPoolExecutor(max_workers=2)

# Configure Windows Tesseract Path
# Assuming standard installation path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCREngine:
    def __init__(self):
        pass

    def preprocess_for_ocr(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Prepares an image for Tesseract to improve accuracy.
        Converts to grayscale and applies thresholding.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Apply Otsu's thresholding to binarize the image (black text on white background)
        # This helps Tesseract distinguish characters from UI backgrounds
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def extract_text(self, img_bgr: np.ndarray, config: str = '--psm 3') -> str:
        """
        Extracts raw text from an image.
        PSM 3 is default (Fully automatic page segmentation).
        PSM 6 is good for a single uniform block of text.
        PSM 11 is good for sparse text (like finding a specific button label).
        """
        try:
            processed = self.preprocess_for_ocr(img_bgr)
            text = pytesseract.image_to_string(processed, config=config)
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract-OCR is not installed or not in the system PATH.")
            return "[OCR Error: Tesseract not found]"
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""

    async def extract_text_async(self, image_bgr: np.ndarray) -> str:
        """
        Non-blocking wrapper that runs the heavy OCR process in a separate thread.
        Crucial for maintaining GUI and WebSocket responsiveness.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(vision_pool, self.extract_text, image_bgr)

    def get_text_bounding_boxes(self, img_bgr: np.ndarray) -> list:
        """
        Extracts text along with their (x, y, w, h) coordinates.
        Useful for clicking exactly on a word.
        """
        try:
            processed = self.preprocess_for_ocr(img_bgr)
            # image_to_data returns a structured string/dict of words and coordinates
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            
            boxes = []
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                # If the word is not empty
                text = data['text'][i].strip()
                if text:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    # Also include confidence score
                    conf = int(data['conf'][i])
                    
                    if conf > 40: # Filter out very low confidence garbage
                        boxes.append({
                            "text": text,
                            "x": x, "y": y,
                            "w": w, "h": h,
                            "confidence": conf
                        })
            return boxes

        except Exception as e:
            logger.error(f"Failed to get OCR bounding boxes: {str(e)}")
            return []

# Singleton instance
ocr_engine = OCREngine()

"""
==================================================
REETA — vision/screen_capture.py
==================================================
PURPOSE:
    Provides ultra-fast screen capture using mss.
    Returns numpy arrays for immediate OpenCV processing.
==================================================
"""

import mss
import numpy as np
import cv2
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("vision.screen_capture")

# Directory for storing raw screenshots (for debugging or visual memory)
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        # Monitor 1 is usually the primary display
        self.monitor = self.sct.monitors[1]

    def capture_full_screen(self, save_to_disk: bool = False) -> np.ndarray:
        """
        Captures the entire primary monitor.
        Returns the image as an OpenCV-compatible BGR numpy array.
        """
        try:
            # Grab the raw pixels
            sct_img = self.sct.grab(self.monitor)
            
            # Convert mss object to numpy array (BGRA)
            img_bgra = np.array(sct_img)
            
            # Convert BGRA to BGR (standard OpenCV format)
            img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)

            if save_to_disk:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SCREENSHOT_DIR, f"capture_{timestamp}.png")
                cv2.imwrite(filename, img_bgr)
                logger.debug(f"Saved screenshot to {filename}")

            return img_bgr

        except Exception as e:
            logger.error(f"Failed to capture screen: {str(e)}")
            return None

    def capture_region(self, left: int, top: int, width: int, height: int) -> np.ndarray:
        """
        Captures a specific region of the screen.
        """
        try:
            region = {"top": top, "left": left, "width": width, "height": height}
            sct_img = self.sct.grab(region)
            img_bgra = np.array(sct_img)
            img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA@BGR)
            return img_bgr
        except Exception as e:
            logger.error(f"Failed to capture region: {str(e)}")
            return None

# Singleton instance
screen_capturer = ScreenCapture()

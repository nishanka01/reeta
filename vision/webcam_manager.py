"""
==================================================
REETA — vision/webcam_manager.py
==================================================
PURPOSE:
    Captures frames from the local webcam for visual scene analysis.
==================================================
"""

import cv2
import numpy as np
from utils.logger import get_logger

logger = get_logger("vision.webcam")

class WebcamManager:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        # We don't keep the camera open constantly to save resources and respect privacy.
        # We only open it when a frame is requested.

    def capture_frame(self) -> np.ndarray:
        """
        Opens the webcam, captures a single frame, and immediately releases it.
        Returns the frame as a BGR numpy array.
        """
        logger.info("Accessing webcam to capture frame...")
        
        # Open video capture device
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            logger.error("Could not open webcam.")
            return None

        # Read a single frame
        ret, frame = cap.read()
        
        # Release the camera immediately
        cap.release()

        if not ret:
            logger.error("Failed to grab frame from webcam.")
            return None

        logger.debug("Successfully captured webcam frame.")
        return frame

    def check_camera_availability(self) -> bool:
        """
        Quick check if the camera is accessible.
        """
        cap = cv2.VideoCapture(self.camera_index)
        is_open = cap.isOpened()
        if is_open:
            cap.release()
        return is_open

# Singleton instance
webcam_manager = WebcamManager()

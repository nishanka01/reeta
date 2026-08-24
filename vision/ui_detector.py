"""
==================================================
REETA — vision/ui_detector.py
==================================================
PURPOSE:
    Detects specific UI elements (icons, buttons) on the screen
    using OpenCV template matching.
==================================================
"""

import cv2
import numpy as np
import os
from utils.logger import get_logger

logger = get_logger("vision.ui_detector")

class UIDetector:
    def __init__(self):
        # We assume there might be a directory of known UI templates
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vision_templates")
        os.makedirs(self.templates_dir, exist_ok=True)

    def find_template_on_screen(self, screen_bgr: np.ndarray, template_name: str, threshold: float = 0.8) -> dict:
        """
        Looks for a saved UI element template inside the given screen image.
        Returns the center coordinates if found.
        """
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            logger.error(f"Template not found: {template_path}")
            return None

        # Load the template image
        template_bgr = cv2.imread(template_path)
        if template_bgr is None:
            logger.error(f"Failed to load template: {template_path}")
            return None

        # Get dimensions of the template
        h, w = template_bgr.shape[:2]

        # Use OpenCV's matchTemplate to slide the template across the screen
        # TM_CCOEFF_NORMED is robust to slight lighting changes
        res = cv2.matchTemplate(screen_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
        
        # Find the best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # max_loc gives the top-left corner of the match
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            # Calculate the center point for clicking
            center_x = top_left[0] + w // 2
            center_y = top_left[1] + h // 2

            logger.info(f"Found '{template_name}' with confidence {max_val:.2f} at center ({center_x}, {center_y})")
            return {
                "found": True,
                "confidence": max_val,
                "center_x": center_x,
                "center_y": center_y,
                "bbox": {"left": top_left[0], "top": top_left[1], "width": w, "height": h}
            }
        else:
            logger.debug(f"Template '{template_name}' not found. Max confidence: {max_val:.2f}")
            return {"found": False, "confidence": max_val}

# Singleton instance
ui_detector = UIDetector()

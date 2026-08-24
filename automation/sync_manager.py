"""
==================================================
REETA — automation/sync_manager.py
==================================================
PURPOSE:
    Ensures that the desktop environment is synchronized
    with REETA's expectations before performing actions.
    (e.g., verifying the correct window is in focus).
==================================================
"""

import time
from utils.logger import get_logger

try:
    import pygetwindow as gw
except ImportError:
    pass

logger = get_logger(__name__)

class SyncManager:
    """Manages automation pacing and active window verification."""

    @staticmethod
    def wait_for_window_focus(window_title_keyword: str, timeout: float = 5.0) -> bool:
        """
        Pauses execution until a window containing the keyword is active.
        Returns True if successful, False if it times out.
        """
        logger.debug(f"Waiting for window focus containing: '{window_title_keyword}'")
        start_time = time.time()
        keyword_lower = window_title_keyword.lower()

        while time.time() - start_time < timeout:
            try:
                active_window = gw.getActiveWindow()
                if active_window and active_window.title:
                    if keyword_lower in active_window.title.lower():
                        logger.info(f"Verified focus on: {active_window.title}")
                        return True
            except Exception as e:
                logger.debug(f"Error checking active window: {e}")
            
            time.sleep(0.5)

        logger.warning(f"Timeout waiting for window focus: '{window_title_keyword}'")
        return False

    @staticmethod
    def ensure_safe_pacing(action_name: str, delay: float = 0.5):
        """
        Enforces a minimum delay before taking an action to let UI settle.
        """
        logger.debug(f"Pacing automation for: {action_name}")
        time.sleep(delay)

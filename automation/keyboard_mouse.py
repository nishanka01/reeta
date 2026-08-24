"""
==================================================
REETA — automation/keyboard_mouse.py
==================================================
PURPOSE:
    Provides wrappers around PyAutoGUI for mouse and keyboard.
    Includes a fail-safe kill switch.
==================================================
"""

from utils.logger import get_logger
from automation.sync_manager import SyncManager

try:
    import pyautogui
    import keyboard # Used for global hotkeys (kill switch)
    
    # Safety: moving mouse to any corner of the screen aborts PyAutoGUI
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5 # 0.5s pause after every action
    
except ImportError:
    pass

logger = get_logger(__name__)

class InputController:
    """Manages virtual keyboard and mouse inputs."""
    
    def __init__(self):
        self.kill_switch_active = False
        logger.info("InputController initialized with PyAutoGUI failsafe enabled.")

    def _check_failsafe(self):
        """Raises exception if kill switch is engaged."""
        if self.kill_switch_active:
            raise RuntimeError("AUTOMATION ABORTED BY KILL SWITCH.")

    def type_text(self, text: str, hit_enter: bool = False):
        """Types text out like a human."""
        self._check_failsafe()
        SyncManager.ensure_safe_pacing("type_text", delay=0.5)
        try:
            logger.info(f"Typing text: {text[:20]}...")
            pyautogui.write(text, interval=0.05)
            if hit_enter:
                pyautogui.press('enter')
            return "Finished typing."
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return "Failed to type text."

    def press_shortcut(self, *keys):
        """Presses a combination of keys (e.g. 'ctrl', 'c')."""
        self._check_failsafe()
        SyncManager.ensure_safe_pacing("press_shortcut", delay=0.2)
        try:
            pyautogui.hotkey(*keys)
            return f"Pressed {' + '.join(keys)}."
        except Exception as e:
            logger.error(f"Shortcut failed: {e}")
            return "Failed to press shortcut."

    def click_screen(self, x: int, y: int, right_click: bool = False):
        """Clicks at a specific coordinate."""
        self._check_failsafe()
        SyncManager.ensure_safe_pacing("click_screen", delay=0.2)
        try:
            if right_click:
                pyautogui.rightClick(x, y)
            else:
                pyautogui.click(x, y)
            return "Clicked."
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return "Failed to click."

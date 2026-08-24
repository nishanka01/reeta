"""
==================================================
REETA — automation/app_control.py
==================================================
PURPOSE:
    Advanced application control using psutil and pygetwindow.
    Can launch, focus, and close applications.
==================================================
"""

import os
import subprocess
from pathlib import Path
from utils.logger import get_logger
from automation.safety_manager import SafetyManager

try:
    import psutil
    import pygetwindow as gw
except ImportError:
    pass

logger = get_logger(__name__)

# Common app paths for quick launching
WINDOWS_APPS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "vscode": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "notepad": [r"C:\Windows\System32\notepad.exe"],
    "calculator": ["calc.exe"],
    "spotify": [os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")],
}

class AppController:
    """Manages OS-level applications and windows."""
    
    def __init__(self):
        logger.info("AppController initialized")

    def open_application(self, app_name: str) -> str:
        """Launch a desktop application by name."""
        app_key = app_name.lower().strip()
        logger.info(f"Opening application: {app_name}")

        if app_key not in WINDOWS_APPS:
            return self._try_system_launch(app_name)

        for exe_path in WINDOWS_APPS[app_key]:
            try:
                p = Path(exe_path)
                if p.is_absolute() and not p.exists():
                    continue
                subprocess.Popen(
                    [str(exe_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.DETACHED_PROCESS,
                )
                return f"Opening {app_name}."
            except Exception as e:
                logger.debug(f"Failed path {exe_path}: {e}")
                continue

        return self._try_system_launch(app_name)

    def _try_system_launch(self, app_name: str) -> str:
        """Try launching via system PATH."""
        try:
            exe = app_name if app_name.endswith(".exe") else f"{app_name}.exe"
            subprocess.Popen(
                [exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS,
            )
            return f"Opening {app_name}."
        except Exception as e:
            msg = f"Failed to open {app_name}: {e}"
            logger.error(msg)
            return msg

    def close_application(self, app_name: str) -> str:
        """Close an application gracefully."""
        # Safety check: We don't want to accidentally close critical processes
        if app_name.lower() in ["explorer", "system", "svchost"]:
            return f"I am not allowed to close {app_name}."
            
        closed = False
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed = True
            if closed:
                return f"Closed {app_name}."
            return f"I couldn't find {app_name} running."
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return f"Failed to close {app_name}."

    def focus_window(self, window_title: str) -> str:
        """Brings a window to the foreground."""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                return f"Focused on {window_title}."
            return f"Could not find a window matching {window_title}."
        except Exception as e:
            logger.error(f"Failed to focus window: {e}")
            return f"Failed to focus window {window_title}."

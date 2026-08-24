"""
==================================================
REETA — automation/file_manager.py
==================================================
PURPOSE:
    Handles safe file and directory operations.
    Enforces policies using SafetyManager.
==================================================
"""

import os
import shutil
from pathlib import Path
from utils.logger import get_logger
from automation.safety_manager import SafetyManager

logger = get_logger(__name__)

class FileManager:
    """Automates file system operations safely."""
    
    def __init__(self):
        # Default working directory is Desktop
        self.working_dir = Path.home() / "Desktop"
    
    def _resolve_path(self, target: str) -> Path:
        """Resolves relative paths to the working directory."""
        p = Path(target)
        if not p.is_absolute():
            return self.working_dir / p
        return p

    def create_folder(self, folder_name: str) -> str:
        """Creates a new directory."""
        try:
            target = self._resolve_path(folder_name)
            
            if not SafetyManager.is_path_safe(target):
                return f"Cannot create folder at restricted path: {target}"
                
            target.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {target}")
            return f"Created folder {folder_name}."
        except Exception as e:
            logger.error(f"Failed to create folder {folder_name}: {e}")
            return f"Failed to create folder."

    def delete_file(self, file_path: str, confirmed: bool = False) -> str:
        """Deletes a file, requiring confirmation for safety."""
        target = self._resolve_path(file_path)
        
        if not SafetyManager.is_path_safe(target):
            return f"Deletion blocked by safety policy: {target}"
            
        if not target.exists():
            return f"Could not find {file_path} to delete."

        if not confirmed:
            return f"CONFIRM_REQUIRED:delete_file:{target}"

        try:
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            logger.info(f"Deleted {target}")
            return f"Deleted {target.name}."
        except Exception as e:
            logger.error(f"Delete failed for {target}: {e}")
            return f"Failed to delete."

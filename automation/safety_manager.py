"""
==================================================
REETA — automation/safety_manager.py
==================================================
PURPOSE:
    Provides critical safety guardrails for desktop automation.
    Prevents REETA from deleting system files or performing
    unauthorized destructive actions.
==================================================
"""

import os
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

class SafetyManager:
    """
    Validates automation commands against safety policies.
    """

    # Directories that REETA is absolutely forbidden from modifying
    RESTRICTED_DIRECTORIES = [
        Path(r"C:\Windows").resolve(),
        Path(r"C:\Program Files").resolve(),
        Path(r"C:\Program Files (x86)").resolve(),
        Path(os.environ.get("SystemRoot", r"C:\Windows")).resolve(),
    ]

    # Actions that require explicit user confirmation
    DESTRUCTIVE_ACTIONS = [
        "delete_file",
        "delete_folder",
        "format_drive",
        "send_email",
        "close_unsaved_app"
    ]

    @classmethod
    def is_path_safe(cls, target_path: str | Path) -> bool:
        """
        Checks if a file path is safe to modify/delete.
        """
        try:
            target = Path(target_path).resolve()
            
            # Root drive check (e.g., C:\)
            if target.parent == target:
                logger.warning(f"Safety constraint violation: Attempted to modify root drive {target}")
                return False

            # Check against restricted directories
            for restricted in cls.RESTRICTED_DIRECTORIES:
                # If the target is inside a restricted directory, block it
                if target.is_relative_to(restricted):
                    logger.warning(f"Safety constraint violation: Attempted to modify protected path {target}")
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"Safety path validation failed: {e}")
            return False # Fail safe

    @classmethod
    def requires_confirmation(cls, action_type: str) -> bool:
        """
        Returns True if the action requires verbal/text confirmation from the user.
        """
        return action_type in cls.DESTRUCTIVE_ACTIONS

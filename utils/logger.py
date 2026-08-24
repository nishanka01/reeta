"""
==================================================
REETA — utils/logger.py
==================================================
PURPOSE:
    Professional logging system for REETA.
    Every module uses this logger to record what's happening —
    commands received, errors caught, actions taken.

HOW IT WORKS:
    1. Creates a root logger named "reeta"
    2. Outputs to BOTH console (colorized) and file (logs/reeta.log)
    3. Console shows INFO+ level, file captures DEBUG+ level
    4. File auto-rotates at 5MB to prevent disk bloat
    5. Each module calls: logger = get_logger(__name__)

WHY THIS MATTERS:
    - When something breaks, logs tell you exactly what happened
    - Color-coded console output makes it easy to spot errors
    - File logs persist for debugging after crashes
    - Named loggers show which module each message came from
==================================================
"""

import logging
import sys
import json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Import colorama for colored console output on Windows
try:
    from colorama import init, Fore, Style
    init(autoreset=True)  # Auto-reset colors after each print
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


# ── Color Mapping for Log Levels ────────────────────────────
# Maps log levels to colorama colors for easy visual scanning
LEVEL_COLORS = {
    "DEBUG": Fore.CYAN if COLORAMA_AVAILABLE else "",
    "INFO": Fore.GREEN if COLORAMA_AVAILABLE else "",
    "WARNING": Fore.YELLOW if COLORAMA_AVAILABLE else "",
    "ERROR": Fore.RED if COLORAMA_AVAILABLE else "",
    "CRITICAL": Fore.RED + Style.BRIGHT if COLORAMA_AVAILABLE else "",
}
RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else ""


class ColoredConsoleFormatter(logging.Formatter):
    """
    Custom formatter that adds color to console log output.

    Example output:
        [12:34:56] ✅ INFO  | voice.listener | Whisper model loaded
        [12:34:57] ❌ ERROR | brain.llm      | API key invalid
    """

    # Emoji indicators for quick visual scanning
    LEVEL_ICONS = {
        "DEBUG": "🔍",
        "INFO": "✅",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Get color and icon for this log level
        color = LEVEL_COLORS.get(record.levelname, "")
        icon = self.LEVEL_ICONS.get(record.levelname, "")

        # Shorten the module name for cleaner output
        # e.g., "voice.listener" instead of "REETA.voice.listener"
        module_name = record.name.replace("reeta.", "")
        if len(module_name) > 20:
            module_name = module_name[:20]

        # Format the timestamp
        timestamp = self.formatTime(record, "%H:%M:%S")

        # Build the colored message
        formatted = (
            f"{color}[{timestamp}] {icon} {record.levelname:<8}{RESET}"
            f" | {color}{module_name:<20}{RESET}"
            f" | {record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            formatted += f"\n{color}{self.formatException(record.exc_info)}{RESET}"

        return formatted


class FileFormatter(logging.Formatter):
    """
    Clean formatter for log files (no colors, no emojis).
    Includes full timestamp with date for historical analysis.

    Example output:
        2025-01-15 12:34:56 | INFO     | voice.listener | Whisper model loaded
    """

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs logs as JSON lines for automated ingestion.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Broadcast to UI
        try:
            from api.websocket_manager import sync_broadcast
            sync_broadcast("LOG_EVENT", log_data)
        except Exception:
            pass
            
        return json.dumps(log_data)


def setup_root_logger(log_dir: Path) -> logging.Logger:
    """
    Set up the root 'reeta' logger with console and file handlers.

    This is called ONCE at startup. All child loggers (voice.listener,
    brain.llm_handler, etc.) inherit this configuration automatically.

    Args:
        log_dir: Path to the logs directory

    Returns:
        The configured root logger
    """
    # Create the root logger for REETA
    root_logger = logging.getLogger("reeta")
    root_logger.setLevel(logging.DEBUG)  # Capture everything

    # Prevent duplicate handlers if called multiple times
    if root_logger.handlers:
        return root_logger

    # ── Console Handler ─────────────────────────────────────
    # Shows INFO and above in the terminal (colored)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredConsoleFormatter())
    root_logger.addHandler(console_handler)

    # ── File Handler ────────────────────────────────────────
    # Saves DEBUG and above to logs/reeta.log
    # Rotates at 5MB, keeps last 3 log files
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "reeta.log"

    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,             # Keep reeta.log.1, .2, .3
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Use JSON formatting if enabled in settings
    try:
        from config.settings import settings
        use_json = settings.ENABLE_JSON_LOGS
    except ImportError:
        use_json = False
        
    if use_json:
        file_handler.setFormatter(JsonFormatter())
    else:
        file_handler.setFormatter(FileFormatter())
        
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a named logger for a specific module.

    Usage in any module:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
        logger.error("Something broke", exc_info=True)

    Args:
        module_name: Usually __name__, e.g., "voice.listener"

    Returns:
        A logger instance that inherits the root reeta configuration
    """
    # Prefix with "reeta." so all loggers are children of the root
    if not module_name.startswith("reeta."):
        logger_name = f"reeta.{module_name}"
    else:
        logger_name = module_name

    return logging.getLogger(logger_name)

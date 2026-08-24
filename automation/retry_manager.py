"""
==================================================
REETA — automation/retry_manager.py
==================================================
PURPOSE:
    Provides robust retry mechanisms specifically designed
    for desktop and browser automation where timing is flaky.
==================================================
"""

import time
import functools
from typing import Callable, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class AutomationRetryException(Exception):
    pass

def with_automation_retry(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator for UI automation tasks.
    Unlike network retries, UI retries often need longer base delays
    and linear or small exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_retries:
                        logger.error(f"Automation step '{func.__name__}' failed permanently after {max_retries} attempts: {e}")
                        raise AutomationRetryException(f"Failed to execute {func.__name__}") from e
                    
                    delay = base_delay * attempt
                    logger.warning(f"Automation step '{func.__name__}' failed (Attempt {attempt}/{max_retries}). Retrying in {delay}s... ({e})")
                    time.sleep(delay)
        return wrapper
    return decorator

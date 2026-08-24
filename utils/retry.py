"""
==================================================
REETA — utils/retry.py
==================================================
PURPOSE:
    Provides an exponential backoff retry decorator for
    API calls and unstable network operations.

HOW IT WORKS:
    @with_retry(max_retries=3, base_delay=1.0)
    def my_flaky_function(): ...
==================================================
"""

import time
import functools
from utils.logger import get_logger

logger = get_logger(__name__)

def with_retry(max_retries: int = 3, base_delay: float = 1.0, exceptions=(Exception,)):
    """
    Exponential backoff retry decorator.
    
    Args:
        max_retries: Number of times to retry before giving up.
        base_delay: Initial delay in seconds. Multiplies by 2 each attempt.
        exceptions: Tuple of exception types to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
            
            # If we exhausted retries, raise the last exception
            raise last_exception
        return wrapper
    return decorator

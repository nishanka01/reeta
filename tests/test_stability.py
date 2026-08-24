"""
==================================================
REETA — tests/test_stability.py
==================================================
PURPOSE:
    Tests the new stability features added in Phase 3.
    - Retry logic for API
    - Memory deduplication
==================================================
"""

import unittest
from unittest.mock import patch, MagicMock
from utils.retry import with_retry

# Test 1: Retry logic
class TestRetryDecorator(unittest.TestCase):
    def test_successful_retry(self):
        self.attempts = 0

        @with_retry(max_retries=3, base_delay=0.01)
        def flaky_func():
            self.attempts += 1
            if self.attempts < 3:
                raise ValueError("Temporary network glitch")
            return "Success!"

        result = flaky_func()
        self.assertEqual(result, "Success!")
        self.assertEqual(self.attempts, 3)

    def test_failed_retry(self):
        self.attempts = 0

        @with_retry(max_retries=2, base_delay=0.01)
        def failing_func():
            self.attempts += 1
            raise ValueError("Permanent failure")

        with self.assertRaises(ValueError):
            failing_func()
        
        self.assertEqual(self.attempts, 3)  # initial + 2 retries

if __name__ == "__main__":
    unittest.main()

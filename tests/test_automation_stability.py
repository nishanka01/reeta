"""
==================================================
REETA — tests/test_automation_stability.py
==================================================
PURPOSE:
    Tests the new stabilization features (Phase 3.5).
    Verifies retry logic, sync manager, and fail-fast engine.
==================================================
"""

import unittest
from unittest.mock import patch, MagicMock
from automation.retry_manager import with_automation_retry, AutomationRetryException
from automation.workflow_engine import WorkflowEngine

class TestRetryManager(unittest.TestCase):
    def test_automation_retry_success(self):
        self.attempts = 0

        @with_automation_retry(max_retries=3, base_delay=0.01)
        def flaky_ui_action():
            self.attempts += 1
            if self.attempts < 3:
                raise ValueError("UI element not ready")
            return "Clicked"

        result = flaky_ui_action()
        self.assertEqual(result, "Clicked")
        self.assertEqual(self.attempts, 3)

    def test_automation_retry_failure(self):
        self.attempts = 0

        @with_automation_retry(max_retries=2, base_delay=0.01)
        def failing_ui_action():
            self.attempts += 1
            raise ValueError("Browser crashed")

        with self.assertRaises(AutomationRetryException):
            failing_ui_action()
        
        self.assertEqual(self.attempts, 2)

class TestFailFastWorkflowEngine(unittest.TestCase):
    @patch('automation.app_control.AppController.open_application')
    @patch('automation.browser_control.BrowserController.search_google')
    def test_fail_fast(self, mock_search, mock_open):
        # Simulate an app launch failure
        mock_open.return_value = "Failed to open notepad."
        
        engine = WorkflowEngine()
        steps = [
            {"action": "open_app", "target": "notepad"},
            {"action": "web_search", "target": "cute cats"} # Should NOT execute
        ]
        
        result = engine.execute_steps(steps)
        
        self.assertIn("Workflow failed at step 1", result)
        mock_open.assert_called_once_with("notepad")
        mock_search.assert_not_called()

if __name__ == "__main__":
    unittest.main()

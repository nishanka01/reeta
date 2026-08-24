"""
==================================================
REETA — tests/test_automation.py
==================================================
PURPOSE:
    Tests for the automation logic, particularly the safety manager
    and the workflow engine.
==================================================
"""

import unittest
from pathlib import Path
from automation.safety_manager import SafetyManager
from automation.workflow_engine import WorkflowEngine

class TestSafetyManager(unittest.TestCase):
    def test_restricted_directories(self):
        """Ensure restricted directories are correctly blocked."""
        # Windows directory should be blocked
        self.assertFalse(SafetyManager.is_path_safe(r"C:\Windows\System32\cmd.exe"))
        
        # Root drive should be blocked
        self.assertFalse(SafetyManager.is_path_safe(r"C:\\"))
        
        # Desktop should be allowed
        self.assertTrue(SafetyManager.is_path_safe(Path.home() / "Desktop" / "test.txt"))

    def test_confirmation_required(self):
        """Ensure destructive actions require confirmation."""
        self.assertTrue(SafetyManager.requires_confirmation("delete_file"))
        self.assertTrue(SafetyManager.requires_confirmation("format_drive"))
        self.assertFalse(SafetyManager.requires_confirmation("open_app"))

class TestWorkflowEngine(unittest.TestCase):
    def test_empty_workflow(self):
        engine = WorkflowEngine()
        result = engine.execute_steps([])
        self.assertEqual(result, "I couldn't figure out how to do that.")

    # We won't test full execution here as it would actually open apps/browsers
    # in the CI/CD pipeline, which is not desired.

if __name__ == "__main__":
    unittest.main()

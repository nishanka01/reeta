"""
==================================================
REETA — commands/automation_router.py
==================================================
PURPOSE:
    Intercepts commands that look like desktop automation tasks.
    If valid, parses them and executes the workflow.
==================================================
"""

from utils.logger import get_logger
from commands.command_parser import CommandParser
from automation.workflow_engine import WorkflowEngine
from brain.llm_handler import LLMHandler

logger = get_logger(__name__)

class AutomationRouter:
    """Detects and routes automation commands."""

    def __init__(self, llm_handler: LLMHandler):
        self.parser = CommandParser(llm_handler)
        self.engine = WorkflowEngine()

        # Keywords that strongly imply an automation task
        self.automation_keywords = [
            "open", "close", "launch", "start", "search for", 
            "google", "type", "click", "create folder", "delete file"
        ]

    def is_automation_command(self, text: str) -> bool:
        """Heuristics to check if the user wants an action done."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.automation_keywords)

    def process(self, text: str) -> str:
        """Parses the text and executes the workflow steps."""
        logger.info(f"Routing automation command: {text}")
        
        # 1. Parse natural language into discrete steps
        steps = self.parser.parse_workflow(text)
        
        if not steps:
            return "I understood that as an action, but I'm not sure how to execute it."
            
        # 2. Execute the steps
        return self.engine.execute_steps(steps)

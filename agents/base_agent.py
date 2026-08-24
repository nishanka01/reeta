"""
==================================================
REETA — agents/base_agent.py
==================================================
PURPOSE:
    Provides a common interface and utility methods for all REETA agents.
    Every specialized agent inherits from BaseAgent.
==================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.logger import get_logger

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"agent.{self.name}")

    @abstractmethod
    def run(self, state: dict) -> dict:
        """
        Executes the agent's core logic.
        Receives the global GraphState, returns a dictionary of updates to be merged into the state.
        """
        pass

    def log_action(self, action: str):
        """Standardized logging for agent actions."""
        self.logger.info(f"[{self.name}] {action}")

    def error_recovery(self, error: Exception) -> dict:
        """Standardized error handling to prevent graph crashes."""
        self.logger.error(f"[{self.name}] Execution failed: {str(error)}")
        return {
            "errors": [f"[{self.name}] {str(error)}"],
            # Important: always return current_agent so orchestrator knows who failed
            "current_agent": self.name 
        }

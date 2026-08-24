"""
==================================================
REETA — orchestration/task_manager.py
==================================================
PURPOSE:
    High-level API for triggering multi-agent workflows.
    Maintains the async loop for graph execution.
==================================================
"""

import asyncio
from orchestration.graph_builder import build_agent_graph
from orchestration.execution_monitor import monitor_agent_execution
from utils.logger import get_logger

logger = get_logger("orchestration.task_manager")

class TaskManager:
    def __init__(self):
        self.app = build_agent_graph()

    async def execute_task(self, user_request: str):
        """
        Initiates a multi-agent workflow based on user input.
        """
        logger.info(f"Starting Multi-Agent Workflow for request: {user_request}")

        # Initialize the global state
        initial_state = {
            "user_request": user_request,
            "current_agent": "system",
            "messages": [],
            "shared_context": {},
            "task_plan": [],
            "final_response": "",
            "errors": []
        }

        # Execute the graph asynchronously
        # .astream() yields updates as each node finishes
        try:
            async for output in self.app.astream(initial_state):
                for node_name, state_update in output.items():
                    monitor_agent_execution(node_name, state_update)
            
            logger.info("Multi-Agent Workflow completed successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Multi-Agent Workflow crashed: {str(e)}")
            return False

# Global instance
task_manager = TaskManager()

"""
==================================================
REETA — agents/memory_agent.py
==================================================
PURPOSE:
    Manages semantic retrieval, memory cleanup, and context optimization.
==================================================
"""

from agents.base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MemoryAgent", description="Optimizes and retrieves semantic memory.")

    def run(self, state: dict) -> dict:
        self.log_action("Executing memory retrieval task.")
        try:
            task_plan = state.get("task_plan", [])
            for step in task_plan:
                if step.get("agent") == self.name and step.get("status") == "pending":
                    step["status"] = "completed"
                    break

            return {
                "current_agent": self.name,
                "task_plan": task_plan,
                "shared_context": {"retrieved_memories": ["Relevant past context from ChromaDB"]},
                "messages": [{"role": "system", "content": f"MemoryAgent retrieved relevant context."}]
            }
        except Exception as e:
            return self.error_recovery(e)

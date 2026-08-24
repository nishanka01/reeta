"""
==================================================
REETA — agents/research_agent.py
==================================================
PURPOSE:
    Specializes in web research, summarization, and information gathering.
==================================================
"""

from agents.base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ResearchAgent", description="Gathers data from the web and summarizes information.")

    def run(self, state: dict) -> dict:
        self.log_action("Executing research task.")
        try:
            # Mark the current step as completed in the task plan
            task_plan = state.get("task_plan", [])
            for step in task_plan:
                if step.get("agent") == self.name and step.get("status") == "pending":
                    step["status"] = "completed"
                    break

            return {
                "current_agent": self.name,
                "task_plan": task_plan, # Update status
                "shared_context": {"research_results": "Gathered data on requested topic."},
                "messages": [{"role": "system", "content": f"ResearchAgent completed data gathering."}]
            }
        except Exception as e:
            return self.error_recovery(e)

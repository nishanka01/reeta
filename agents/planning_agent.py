"""
==================================================
REETA — agents/planning_agent.py
==================================================
PURPOSE:
    The Coordinator. Analyzes the user's request, breaks it into steps, 
    and determines which agent should run next.
==================================================
"""

from agents.base_agent import BaseAgent
# In a real setup, you'd import your LLM client here
# from brain.ai_brain import get_llm_response

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PlanningAgent", description="Coordinates task execution and routing.")

    def run(self, state: dict) -> dict:
        self.log_action("Analyzing current state to determine next steps.")
        
        try:
            user_request = state.get("user_request", "")
            task_plan = state.get("task_plan", [])
            messages = state.get("messages", [])

            # --- Mock LLM Logic for Phase 5 Setup ---
            # In production, we pass the user_request and state to Gemini/Claude
            # to generate a structured JSON plan.
            
            if not task_plan:
                self.log_action("Creating initial execution plan.")
                # Basic heuristic routing (to be replaced by LLM)
                if "research" in user_request.lower() or "search" in user_request.lower():
                    next_agent = "ResearchAgent"
                elif "screen" in user_request.lower() or "read" in user_request.lower() or "look" in user_request.lower() or "vision" in user_request.lower():
                    next_agent = "VisionAgent"
                elif "code" in user_request.lower() or "script" in user_request.lower():
                    next_agent = "CodingAgent"
                elif "automate" in user_request.lower() or "click" in user_request.lower():
                    next_agent = "AutomationAgent"
                elif "security" in user_request.lower() or "scan" in user_request.lower():
                    next_agent = "SecurityAgent"
                else:
                    # Default fallback
                    next_agent = "MemoryAgent"
                
                # Update state
                return {
                    "current_agent": self.name,
                    "task_plan": [{"agent": next_agent, "status": "pending"}],
                    "messages": [{"role": "system", "content": f"PlanningAgent routed task to {next_agent}."}]
                }
            
            # If a plan exists, check if we need to synthesize the final result
            all_done = all(step.get("status") in ["completed", "failed"] for step in task_plan)
            if all_done:
                self.log_action("All tasks completed or failed. Synthesizing final response.")
                return {
                    "current_agent": self.name,
                    "final_response": "Task completed (or failed) based on agent outputs."
                }
                
            # If there are errors from the last agent, mark its task as failed to prevent infinite loop
            errors = state.get("errors", [])
            last_agent = state.get("current_agent")
            if errors and last_agent and last_agent != self.name:
                self.log_action(f"Detected error from {last_agent}. Marking its task as failed.")
                for step in task_plan:
                    if step.get("agent") == last_agent and step.get("status") == "pending":
                        step["status"] = "failed"
                        # Don't return yet, let it re-evaluate all_done on next iteration
                        return {"task_plan": task_plan, "current_agent": self.name}
                        
            # Otherwise, find the next pending task
            for step in task_plan:
                if step.get("status") == "pending":
                    next_agent = step["agent"]
                    self.log_action(f"Routing to next pending agent: {next_agent}")
                    return {
                        "current_agent": self.name,
                        # Don't update the whole list, just route the graph
                        # The router function in graph_builder will read task_plan
                    }

            return {"current_agent": self.name}

        except Exception as e:
            return self.error_recovery(e)

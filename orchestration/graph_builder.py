"""
==================================================
REETA — orchestration/graph_builder.py
==================================================
PURPOSE:
    Constructs the LangGraph state machine. Defines the nodes (agents)
    and edges (routing logic) that govern REETA's autonomous execution.
==================================================
"""

from langgraph.graph import StateGraph, END
from orchestration.state import GraphState
from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent
from agents.automation_agent import AutomationAgent
from agents.memory_agent import MemoryAgent
from agents.security_agent import SecurityAgent
from agents.vision_agent import VisionAgent
from utils.logger import get_logger

logger = get_logger("orchestration.graph")

def build_agent_graph():
    """
    Builds and compiles the Multi-Agent LangGraph.
    """
    logger.info("Building multi-agent LangGraph orchestration...")

    # Initialize agents
    planner = PlanningAgent()
    researcher = ResearchAgent()
    coder = CodingAgent()
    automation = AutomationAgent()
    memory = MemoryAgent()
    security = SecurityAgent()
    vision = VisionAgent()

    # Create Graph
    workflow = StateGraph(GraphState)

    # 1. Add Nodes
    workflow.add_node("planner", planner.run)
    workflow.add_node("researcher", researcher.run)
    workflow.add_node("coder", coder.run)
    workflow.add_node("automation", automation.run)
    workflow.add_node("memory", memory.run)
    workflow.add_node("security", security.run)
    workflow.add_node("vision", vision.run)

    # 2. Add Entry Point
    # Every workflow starts with the planner to break down the task
    workflow.set_entry_point("planner")

    # 3. Add Edges (Routing Logic)
    def route_next_agent(state: GraphState):
        # Guardrail: Prevent infinite routing loops
        step_count = state.get("step_count", 0)
        if step_count > 15:
            logger.error("MAX GRAPH STEPS EXCEEDED. Forcing termination.")
            return "end"

        task_plan = state.get("task_plan", [])
        
        # If everything is done or failed, end the workflow
        if all(step.get("status") in ["completed", "failed"] for step in task_plan):
            return "end"
            
        # Otherwise route to the next pending step
        for step in task_plan:
            if step.get("status") == "pending":
                agent_name = step.get("agent")
                logger.info(f"Orchestrator routing to: {agent_name}")
                
                if agent_name == "ResearchAgent":
                    return "researcher"
                elif agent_name == "CodingAgent":
                    return "coder"
                elif agent_name == "AutomationAgent":
                    return "automation"
                elif agent_name == "MemoryAgent":
                    return "memory"
                elif agent_name == "SecurityAgent":
                    return "security"
                elif agent_name == "VisionAgent":
                    return "vision"
    
        return "end"

    # The planner routes to the appropriate worker agent
    workflow.add_conditional_edges(
        "planner",
        route_next_agent,
        {
            "researcher": "researcher",
            "coder": "coder",
            "automation": "automation",
            "memory": "memory",
            "security": "security",
            "vision": "vision",
            "end": END
        }
    )

    # All worker agents must route back to the planner to determine the next step
    workflow.add_edge("researcher", "planner")
    workflow.add_edge("coder", "planner")
    workflow.add_edge("automation", "planner")
    workflow.add_edge("memory", "planner")
    workflow.add_edge("security", "planner")
    workflow.add_edge("vision", "planner")

    return workflow.compile()

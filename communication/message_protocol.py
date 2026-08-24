"""
==================================================
REETA — communication/message_protocol.py
==================================================
PURPOSE:
    Defines the standard schemas for inter-agent communication.
    Ensures structured, predictable data flow between LLMs.
==================================================
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    """
    Standard message format passed between agents.
    """
    sender: str = Field(description="Name of the agent sending the message (e.g., 'research_agent')")
    receiver: str = Field(description="Name of the target agent, or 'orchestrator'")
    content: str = Field(description="The actual message or result payload")
    action_required: bool = Field(default=False, description="True if the receiver must take an action based on this message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional structured data (e.g., URLs, file paths, confidence scores)")

class TaskDelegation(BaseModel):
    """
    Used by the PlanningAgent to break down tasks.
    """
    task_id: str
    assigned_agent: str
    instructions: str
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must complete before this one")
    status: str = Field(default="pending", description="pending, in_progress, completed, failed")
    result: Optional[str] = None

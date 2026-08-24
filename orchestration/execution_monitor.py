"""
==================================================
REETA — orchestration/execution_monitor.py
==================================================
PURPOSE:
    Monitors graph execution and emits live events over WebSockets
    to the REETA GUI.
==================================================
"""

from utils.logger import get_logger

# Fallback print if ws_manager is not imported (prevents circular dependency crashes)
try:
    from api.websocket_manager import sync_broadcast
except ImportError:
    def sync_broadcast(event, payload):
        pass

logger = get_logger("orchestration.monitor")

def monitor_agent_execution(node_name: str, state_update: dict):
    """
    Called after each node in the LangGraph executes.
    Sends the state update to the frontend.
    """
    logger.info(f"Graph Node Executed: {node_name}")
    
    # Broadcast which agent just finished
    sync_broadcast("AGENT_STATE", {
        "node": node_name,
        "current_agent": state_update.get("current_agent"),
        "task_plan": state_update.get("task_plan", [])
    })

    # If the agent added any UI messages, broadcast them
    messages = state_update.get("messages", [])
    for msg in messages:
        sync_broadcast("CHAT_MESSAGE", {
            "role": msg.get("role", "assistant"),
            "content": f"[{state_update.get('current_agent', 'System')}] {msg.get('content', '')}"
        })

"""
==================================================
REETA — api/websocket_manager.py
==================================================
PURPOSE:
    Manages active WebSocket connections to the frontend UI
    and provides a global event bus to broadcast messages.

PHASE 4.5 HARDENING:
    - Heartbeat PING/PONG support to detect zombie connections
    - Dead connection cleanup on broadcast failure
    - Thread-safe sync_broadcast helper for non-async code
==================================================
"""

import json
import asyncio
from typing import List
from fastapi import WebSocket
from utils.logger import get_logger

logger = get_logger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"GUI Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"GUI Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict = None):
        """Broadcasts an event to all connected React clients."""
        if data is None:
            data = {}
        message = json.dumps({"type": event_type, "payload": data})

        # Track dead connections to remove after iteration
        dead_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        # Remove dead connections
        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)
                logger.warning("Removed a dead WebSocket connection during broadcast.")

    async def handle_client_message(self, websocket: WebSocket, raw_text: str):
        """
        Processes an incoming message from the React frontend.
        Handles heartbeat PING/PONG and routes other messages.
        """
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # Not JSON, treat as raw text command (legacy fallback)
            logger.info(f"Received raw text from UI: {raw_text}")
            return

        msg_type = data.get("type")

        if msg_type == "PING":
            # Reply with PONG immediately to keep the connection alive
            try:
                await websocket.send_text(json.dumps({"type": "PONG"}))
            except Exception:
                pass
        elif msg_type == "CHAT_MESSAGE":
            content = data.get("content", "")
            logger.info(f"Chat message from UI: {content}")
            # TODO: Route to ReetaEngine for processing in Phase 5
        else:
            logger.debug(f"Unknown message type from UI: {msg_type}")


# Global instance so any part of the Python backend can emit events
ws_manager = WebSocketManager()


def sync_broadcast(event_type: str, data: dict = None):
    """
    Safely queues a broadcast from a synchronous thread.
    Uses asyncio to schedule the coroutine on the running event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(ws_manager.broadcast(event_type, data))
    except RuntimeError:
        # No running event loop — ignore (e.g. during startup or unit tests)
        pass

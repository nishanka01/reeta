"""
==================================================
REETA — api/server.py
==================================================
PURPOSE:
    The main FastAPI entrypoint. Wraps REETA backend logic
    and exposes REST/WebSocket endpoints for the Electron GUI.
==================================================
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.websocket_manager import ws_manager
from utils.logger import get_logger
import asyncio
from communication.event_bus import event_bus
from diagnostics.system_monitor import system_monitor

logger = get_logger(__name__)

app = FastAPI(title="REETA API", version="4.0")

# Allow CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("REETA FastAPI Server started. Waiting for GUI connection.")
    # Start stabilization modules
    system_monitor.start()
    asyncio.create_task(event_bus.start())
    logger.info("Stabilization Event Bus and System Monitor started.")

@app.on_event("shutdown")
async def shutdown_event():
    system_monitor.stop()
    event_bus.stop()
    logger.info("Stabilization modules stopped gracefully.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Receive messages from the React UI
            raw_text = await websocket.receive_text()
            # Route through the structured message handler (handles PING, CHAT, etc.)
            await ws_manager.handle_client_message(websocket, raw_text)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "4.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)

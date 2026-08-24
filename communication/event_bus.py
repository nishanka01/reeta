"""
==================================================
REETA — communication/event_bus.py
==================================================
PURPOSE:
    A centralized async Pub/Sub event bus. Decouples agents
    from WebSockets and orchestrators, preventing race conditions
    and allowing reliable broadcasting.
==================================================
"""

import asyncio
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        # Maps event_type (str) to a list of subscriber callbacks
        self.subscribers: Dict[str, List[Callable]] = {}
        # Thread-safe queue for async event processing
        self.queue = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: str, callback: Callable):
        """Register a callback for a specific event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def publish(self, event_type: str, payload: dict):
        """Push an event onto the queue."""
        await self.queue.put({"type": event_type, "payload": payload})

    async def start(self):
        """Background task to process events from the queue."""
        self._running = True
        while self._running:
            try:
                event = await self.queue.get()
                event_type = event["type"]
                payload = event["payload"]
                
                # Notify all subscribers
                if event_type in self.subscribers:
                    for callback in self.subscribers[event_type]:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(payload)
                        else:
                            callback(payload)
                            
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[EventBus Error] Failed to process event: {e}")

    def stop(self):
        """Stops the event loop processor."""
        self._running = False

# Singleton instance
event_bus = EventBus()

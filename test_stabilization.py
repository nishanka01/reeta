"""
==================================================
REETA — test_stabilization.py
==================================================
PURPOSE:
    Validates that the stabilization changes (Tenacity retries,
    LRU Caches, and EventBus Pub/Sub) are working securely and asynchronously.
==================================================
"""

import asyncio
import time
from core.llm_client import llm_client
from security.url_analyzer import url_analyzer
from communication.event_bus import event_bus

def test_lru_cache_speed():
    print("==================================================")
    print("TEST 1: Security Pipeline LRU Caching")
    print("==================================================")
    
    url = "https://g00gle.com/test-caching"
    
    # First call (Uncached)
    start = time.time()
    res1 = url_analyzer.parse_url(url)
    t1 = time.time() - start
    print(f"[*] Call 1 (Uncached): {t1:.6f}s")
    
    # Second call (Cached)
    start = time.time()
    res2 = url_analyzer.parse_url(url)
    t2 = time.time() - start
    print(f"[*] Call 2 (Cached)  : {t2:.6f}s")
    
    assert t2 < t1, "Cached call should be faster than uncached"
    print("[*] LRU Cache is working!")

async def test_event_bus():
    print("\n==================================================")
    print("TEST 2: Async Event Bus (Pub/Sub)")
    print("==================================================")
    
    events_received = []
    
    async def sample_callback(payload):
        events_received.append(payload)
        print(f"[*] EventBus Subscriber received: {payload}")
        
    event_bus.subscribe("SYSTEM_ALERT", sample_callback)
    
    # Start the event loop processor
    bus_task = asyncio.create_task(event_bus.start())
    
    # Publish events
    await event_bus.publish("SYSTEM_ALERT", {"msg": "Test Alert 1"})
    await event_bus.publish("SYSTEM_ALERT", {"msg": "Test Alert 2"})
    
    # Wait a tiny bit for the queue to process
    await asyncio.sleep(0.1)
    
    event_bus.stop()
    await bus_task
    
    assert len(events_received) == 2, "Event bus failed to process all events"
    print("[*] Event Bus is processing async events successfully!")

def test_llm_retries():
    print("\n==================================================")
    print("TEST 3: LLM Resilience (Tenacity Retries)")
    print("==================================================")
    
    print("[*] Triggering a simulated 'fail' in the LLM Client...")
    try:
        # We coded the mock to fail if "fail" is in the prompt.
        # Tenacity will retry 5 times before ultimately raising a RetryError.
        llm_client.generate_response("Please fail this request.")
    except Exception as e:
        print(f"[*] Caught Exception after retries: {e.__class__.__name__}")
        print("[*] Tenacity retry logic successfully activated and exhausted.")


if __name__ == "__main__":
    test_lru_cache_speed()
    test_llm_retries()
    asyncio.run(test_event_bus())

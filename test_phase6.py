"""
==================================================
REETA — test_phase6.py
==================================================
PURPOSE:
    Tests the Vision and Screen Intelligence System.
    Ensures screen capture, OCR, and Orchestrator integration work.
==================================================
"""

import asyncio
from vision.screen_capture import screen_capturer
from vision.ocr_engine import ocr_engine
from orchestration.task_manager import task_manager

def test_raw_vision():
    print("==================================================")
    print("TEST 1: Screen Capture & OCR")
    print("==================================================")
    
    # Capture screen
    print("[*] Capturing screen...")
    img = screen_capturer.capture_full_screen(save_to_disk=False)
    if img is None:
        print("[!] Failed to capture screen.")
        return

    print(f"[*] Screen captured successfully. Shape: {img.shape}")
    
    # Run OCR
    print("[*] Running OCR on captured screen (previewing first 200 chars)...")
    text = ocr_engine.extract_text(img)
    if not text:
        print("[!] OCR returned empty or failed.")
    else:
        print(f"[*] OCR Success. Extracted {len(text)} characters.")
        print("-" * 20)
        print(text[:200] + "...\n")
        print("-" * 20)

async def test_agent_integration():
    print("\n==================================================")
    print("TEST 2: Multimodal Agent Integration")
    print("==================================================")
    print("[*] Sending task: 'Read what is on my screen'")
    
    # This should trigger PlanningAgent -> VisionAgent -> PlanningAgent
    await task_manager.execute_task("Read what is on my screen")

if __name__ == "__main__":
    test_raw_vision()
    asyncio.run(test_agent_integration())

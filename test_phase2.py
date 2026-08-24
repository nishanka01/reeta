"""
==================================================
REETA Phase 2 — Memory Verification Script
==================================================
Tests the Memory & Context Intelligence System.
Requires a valid Gemini API key in .env.
==================================================
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from utils.logger import setup_root_logger, get_logger
from brain.llm_handler import LLMHandler

setup_root_logger(settings.LOGS_DIR)
logger = get_logger("test_phase2")

def main():
    print("=" * 60)
    print("  REETA Phase 2 — Memory Test")
    print("=" * 60)
    
    print("\n[1/4] Initializing Brain and Memory System...")
    brain = LLMHandler()
    
    if not brain.memory_manager:
        print("❌ Memory System failed to initialize. Check logs.")
        return
        
    print("  ✅ Memory System Initialized successfully.")
    
    print("\n[2/4] Testing Memory Storage (Async)...")
    # This will trigger the classification, embedding, and storage pipeline
    test_statement = "My favorite color is emerald green."
    print(f"  User says: '{test_statement}'")
    brain.memory_manager.process_interaction_async(test_statement)
    
    # Wait a few seconds for the background thread to classify, embed, and store
    print("  Waiting 5 seconds for background processing...")
    time.sleep(5)
    
    print("\n[3/4] Testing Memory Retrieval...")
    test_question = "What is my favorite color?"
    print(f"  Querying context for: '{test_question}'")
    
    context = brain.memory_manager.get_relevant_context(test_question)
    
    if context:
        print(f"  ✅ Retrieved {len(context)} memories!")
        for i, c in enumerate(context, 1):
            print(f"    Memory {i}: {c}")
    else:
        print("  ⚠️ No relevant memories retrieved. This could mean embedding failed, or the threshold is too strict.")
        
    print("\n[4/4] Testing Full Brain Integration (with LLM)...")
    print(f"  Asking REETA: '{test_question}'")
    
    # Temporarily clear history so the LLM doesn't just read it from immediate chat history
    brain.clear_history()
    
    response = brain.think(test_question)
    print(f"\n  🤖 REETA Response: {response}")
    
    if "emerald green" in response.lower():
        print("\n  ✅ SUCCESS: REETA successfully recalled the fact from long-term memory!")
    else:
        print("\n  ❌ FAIL: REETA did not mention 'emerald green'. Memory injection may have failed.")

    print("\n" + "=" * 60)
    print("  Phase 2 Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

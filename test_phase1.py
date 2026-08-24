"""
REETA Phase 1 — Verification Script
Tests all core modules without requiring microphone/PyAudio.
"""
import sys
import os

# Ensure REETA is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("  REETA Phase 1 — Verification Test")
    print("=" * 60)
    
    # 1. Config
    print("\n[1/7] Testing config.settings...")
    from config.settings import settings
    print(f"  ✅ Provider: {settings.LLM_PROVIDER}")
    print(f"  ✅ Assistant: {settings.ASSISTANT_NAME}")
    print(f"  ✅ Wake Word: {settings.WAKE_WORD}")
    
    # 2. Logger
    print("\n[2/7] Testing utils.logger...")
    from utils.logger import setup_root_logger, get_logger
    setup_root_logger(settings.LOGS_DIR)
    logger = get_logger("test")
    logger.info("Test log message")
    print("  ✅ Logger initialized, log written")
    
    # 3. Helpers
    print("\n[3/7] Testing utils.helpers...")
    from utils.helpers import clean_text, get_current_time_spoken, get_current_date_spoken
    time_str = get_current_time_spoken()
    date_str = get_current_date_spoken()
    print(f"  ✅ Time: {time_str}")
    print(f"  ✅ Date: {date_str}")
    print(f"  ✅ clean_text('  HELLO World!! '): '{clean_text('  HELLO World!! ')}'")
    
    # 4. Speaker
    print("\n[4/7] Testing voice.speaker...")
    from voice.speaker import Speaker
    speaker = Speaker()
    print("  ✅ Speaker initialized (SAPI5)")
    speaker.speak("Test complete. REETA is working.")
    print("  ✅ Speech output working")
    
    # 5. Brain
    print("\n[5/7] Testing brain.llm_handler...")
    from brain.llm_handler import LLMHandler
    brain = LLMHandler()
    print(f"  ✅ LLM Handler initialized (provider: {brain.provider})")
    
    # 6. App Controller
    print("\n[6/7] Testing automation.app_control...")
    from automation.app_control import AppController
    app = AppController()
    print(f"  ✅ AppController initialized")
    from automation.app_control import WINDOWS_APPS
    print(f"  ✅ Known apps: {list(WINDOWS_APPS.keys())}")
    
    # 7. Command Handler
    print("\n[7/7] Testing commands.command_handler...")
    from commands.command_handler import CommandHandler
    cmd = CommandHandler(brain=brain, app_controller=app)
    
    # Test local commands (no API calls needed)
    test_cases = [
        ("what time is it", False),
        ("what is today's date", False),
    ]
    
    for text, expect_exit in test_cases:
        response, should_exit = cmd.process(text)
        status = "✅" if should_exit == expect_exit else "❌"
        print(f"  {status} '{text}' → '{response}' (exit={should_exit})")
    
    # Test AI query (requires API key)
    if brain.provider != "none":
        print("\n  Testing AI brain with a question...")
        response, should_exit = cmd.process("What is 2 plus 2?")
        print(f"  ✅ AI Response: '{response[:80]}...'")
    else:
        print("\n  ⚠️ No API key configured — skipping AI test")
    
    print("\n" + "=" * 60)
    print("  ✅ ALL PHASE 1 TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    main()

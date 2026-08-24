"""
==================================================
REETA — core/engine.py
==================================================
PURPOSE:
    The core engine that runs REETA's main interaction loops.
    Separating this from main.py improves testability and 
    error isolation.
==================================================
"""

import time
from config.settings import settings
from utils.logger import get_logger

try:
    from api.websocket_manager import sync_broadcast
except ImportError:
    def sync_broadcast(event, data=None): pass

logger = get_logger(__name__)

class ReetaEngine:
    """
    Manages the interaction loops for REETA (Voice and Text modes).
    """
    
    def __init__(self, speaker, command_handler, wake_word_detector=None, listener=None):
        self.speaker = speaker
        self.command_handler = command_handler
        self.wake_word_detector = wake_word_detector
        self.listener = listener

    def text_mode_loop(self):
        """
        Interactive Text Mode loop.
        Allows typing commands while retaining the voice output (SAPI5) and desktop control!
        """
        logger.info("Entering Interactive Text Mode loop...")

        greeting = (
            f"Hello! I'm {settings.ASSISTANT_NAME}, your AI desktop assistant. "
            f"I'm running in Text Command Mode with Voice Output enabled. "
            f"Type your command below, and I will help you!"
        )
        print(f"\n💬 {greeting}\n")
        self.speaker.speak(greeting)

        print("=" * 60)
        print(f"  🟢 {settings.ASSISTANT_NAME} is ready and waiting for your text...")
        print(f"  🛑 Type 'exit' or 'goodbye' to quit")
        print("=" * 60 + "\n")

        while True:
            try:
                # Colorized prompt
                from colorama import Fore, Style
                user_text = input(f"{Fore.CYAN}👤 You:{Style.RESET_ALL} ").strip()

                if not user_text:
                    continue

                # Process exit command directly
                from utils.helpers import clean_text
                cleaned = clean_text(user_text)
                if cleaned in ["exit", "quit", "stop", "goodbye", "bye"]:
                    print(f"\n🤖 {settings.ASSISTANT_NAME}: Goodbye! Have a great day.\n")
                    self.speaker.speak("Goodbye! Have a great day.")
                    break

                # Process command
                response, should_exit = self.command_handler.process(user_text)

                print(f"\n🤖 {settings.ASSISTANT_NAME}: {response}\n")
                self.speaker.speak(response)

                if should_exit:
                    break

            except KeyboardInterrupt:
                print("\n\n🛑 Ctrl+C detected. Shutting down...")
                self.speaker.speak("Goodbye! See you next time.")
                break
            except Exception as e:
                logger.error(f"Error in text mode loop: {e}", exc_info=True)
                print(f"\n⚠️  Error: {e}\n")

    def voice_mode_loop(self):
        """
        The main assistant voice loop.
        Runs continuously until the user says "exit" or presses Ctrl+C.
        """
        logger.info("Entering main assistant loop...")

        if not self.wake_word_detector or not self.listener:
            logger.error("Voice mode requires wake_word_detector and listener.")
            return

        # Calibrate microphone for current environment
        print("\n🎤 Calibrating microphone...")
        self.wake_word_detector.calibrate()
        print("✅ Microphone calibrated!\n")

        # Startup greeting
        greeting = (
            f"Hello! I'm {settings.ASSISTANT_NAME}, your AI desktop assistant. "
            f"Say 'Hey {settings.ASSISTANT_NAME}' to wake me up!"
        )
        print(f"💬 {greeting}\n")
        self.speaker.speak(greeting)

        print("=" * 60)
        print(f"  🟢 {settings.ASSISTANT_NAME} is ready and listening...")
        print(f"  💡 Say '{settings.WAKE_WORD}' to activate")
        print(f"  🛑 Say 'exit' or press Ctrl+C to quit")
        print("=" * 60 + "\n")

        while True:
            try:
                # ── Step 1: Wait for wake word ──────────────────
                detected = self.wake_word_detector.listen_for_wake_word()

                if not detected:
                    continue  # No wake word → keep listening

                # ── Step 2: Acknowledge activation ──────────────
                print("\n🎯 Wake word detected! Listening...")
                sync_broadcast("VOICE_STATE", {"state": "listening"})
                self.speaker.speak("Yes?")

                # ── Step 3: Listen for the command ──────────────
                user_text = self.listener.listen_and_transcribe()

                if not user_text:
                    sync_broadcast("VOICE_STATE", {"state": "idle"})
                    self.speaker.speak("I didn't catch that. Please try again.")
                    continue

                print(f"\n👤 You said: \"{user_text}\"")
                sync_broadcast("VOICE_STATE", {"state": "processing"})
                sync_broadcast("CHAT_MESSAGE", {"role": "user", "content": user_text})

                # ── Step 4: Process the command ─────────────────
                response, should_exit = self.command_handler.process(user_text)

                # ── Step 5: Speak the response ──────────────────
                print(f"🤖 {settings.ASSISTANT_NAME}: {response}\n")
                sync_broadcast("CHAT_MESSAGE", {"role": "assistant", "content": response})
                sync_broadcast("VOICE_STATE", {"state": "speaking"})
                self.speaker.speak(response)
                sync_broadcast("VOICE_STATE", {"state": "idle"})

                # ── Step 6: Check for exit ──────────────────────
                if should_exit:
                    logger.info("Exit command received. Shutting down...")
                    break

            except KeyboardInterrupt:
                # User pressed Ctrl+C
                print("\n\n🛑 Ctrl+C detected. Shutting down...")
                self.speaker.speak("Goodbye! See you next time.")
                break

            except Exception as e:
                # Catch any unexpected errors to keep the loop running
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                print(f"\n⚠️  Error: {e}")
                print("Recovering and continuing to listen...\n")
                time.sleep(1)  # Brief pause before resuming

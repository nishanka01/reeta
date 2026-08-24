"""
==================================================
REETA — main.py
==================================================
PURPOSE:
    The entry point and main orchestrator for REETA.
    Ties all modules together into a continuous assistant loop.

MAIN LOOP:
    1. Wait for wake word ("Hey Reeta")
    2. Listen for the user's command
    3. Process the command (local or AI)
    4. Speak the response
    5. Go back to step 1

STARTUP FLOW:
    1. Print banner
    2. Load configuration
    3. Initialize all modules (logger, speaker, listener, brain, etc.)
    4. Calibrate microphone
    5. Enter the main loop

SHUTDOWN:
    - Ctrl+C or saying "exit"/"quit"/"goodbye"
    - Graceful cleanup of all modules
==================================================
"""

import sys
import time

# ── Initialize logging FIRST (before other module imports) ──
from config.settings import settings
from utils.logger import setup_root_logger, get_logger

# Set up the root logger with file and console output
setup_root_logger(settings.LOGS_DIR)
logger = get_logger("main")

# ── Now import all REETA modules ────────────────────────────
from utils.helpers import print_banner, get_system_info
from voice.wakeword import WakeWordDetector
from voice.listener import Listener
from voice.speaker import Speaker
from brain.llm_handler import LLMHandler
from automation.app_control import AppController
from commands.command_handler import CommandHandler
from core.engine import ReetaEngine
from monitoring.health import HealthMonitor
from automation.scheduler import ReetaScheduler


def initialize_modules():
    """
    Initialize all REETA modules in the correct order.

    Returns:
        Tuple of (wake_word_detector, listener, speaker, command_handler)

    The order matters:
    1. Speaker first (needed for startup greeting)
    2. Brain (LLM handler)
    3. App controller
    4. Command handler (needs brain + app controller)
    5. Listener (Whisper model — heaviest, load last)
    6. Wake word detector
    """
    logger.info("Initializing REETA modules...")

    # 1. Text-to-Speech
    logger.info("[1/6] Initializing speaker...")
    speaker = Speaker()

    # 2. AI Brain
    logger.info("[2/6] Initializing AI brain...")
    brain = LLMHandler()

    # 3. App Controller
    logger.info("[3/6] Initializing app controller...")
    app_controller = AppController()

    # 4. Command Handler
    logger.info("[4/6] Initializing command handler...")
    command_handler = CommandHandler(brain=brain, app_controller=app_controller)

    # 5. Speech-to-Text Listener (loads Whisper — may take a moment)
    logger.info("[5/6] Initializing listener (loading Whisper model)...")
    listener = Listener()

    # 6. Wake Word Detector
    logger.info("[6/6] Initializing wake word detector...")
    wake_word_detector = WakeWordDetector()

    logger.info("All modules initialized successfully! ✓")
    return wake_word_detector, listener, speaker, command_handler





def main():
    """
    REETA entry point.

    Handles startup, dynamic mode selection based on PyAudio, and graceful shutdown.
    """
    try:
        # Print the startup banner
        print_banner()

        # Show system info
        sys_info = get_system_info()
        logger.info(
            f"System: {sys_info['os']} {sys_info['os_version']} | "
            f"Python {sys_info['python_version']}"
        )

        # Show configuration
        print(settings)

        # ── Detect PyAudio / SoundDevice Availability ─────
        has_pyaudio = False
        try:
            import pyaudio
            has_pyaudio = True
        except ImportError:
            try:
                import sounddevice
                has_pyaudio = True
            except ImportError:
                pass

        # ── Initialize Core Modules ──────────────────────
        logger.info("Initializing Speaker...")
        speaker = Speaker()

        logger.info("Initializing AI Brain...")
        brain = LLMHandler()

        logger.info("Initializing App Controller...")
        app_controller = AppController()

        logger.info("Initializing Command Handler...")
        cmd_handler = CommandHandler(brain=brain, app_controller=app_controller)

        logger.info("Starting Health Monitor...")
        monitor = HealthMonitor()
        monitor.start()

        logger.info("Starting Proactive Scheduler...")
        scheduler = ReetaScheduler(speaker=speaker)
        scheduler.start()

        if not has_pyaudio:
            print("\n" + "!" * 60)
            print(" [WARNING] PyAudio is not installed (requires C++ tools to compile).")
            print(" Voice input will be disabled, but REETA will still function.")
            print(" Voice Output (Text-to-Speech) is FULLY ENABLED!")
            print("!" * 60 + "\n")
            engine = ReetaEngine(speaker, cmd_handler)
            engine.text_mode_loop()
        else:
            # Let the user choose between Voice Mode and Text Mode
            print("\n" + "=" * 60)
            print("  Select REETA Mode:")
            print("  [1] Voice Mode (Listen with microphone, speak with voice) [DEFAULT]")
            print("  [2] Text Mode (Type commands, speak with voice)")
            print("=" * 60)
            try:
                choice = input("Enter option (1 or 2): ").strip()
            except (KeyboardInterrupt, EOFError):
                choice = "1"

            if choice == "2":
                engine = ReetaEngine(speaker, cmd_handler)
                engine.text_mode_loop()
            else:
                # Initialize STT modules
                logger.info("Initializing listener (loading Whisper model)...")
                listener = Listener()

                logger.info("Initializing wake word detector...")
                wake_word = WakeWordDetector()

                logger.info("All voice modules initialized successfully! ✓")

                # Run the main loop
                engine = ReetaEngine(speaker, cmd_handler, wake_word, listener)
                engine.voice_mode_loop()

    except KeyboardInterrupt:
        print("\n\n[Shutdown] Shutdown requested.")

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\n[X] Fatal error: {e}")
        print("Check logs/reeta.log for details.")
        sys.exit(1)

    finally:
        if 'monitor' in locals():
            monitor.stop()
        if 'scheduler' in locals():
            scheduler.stop()
        print(f"\n[Goodbye] {settings.ASSISTANT_NAME} has shut down.\n")
        logger.info("REETA shut down cleanly.")


# ── Entry Point ─────────────────────────────────────────────
if __name__ == "__main__":
    main()

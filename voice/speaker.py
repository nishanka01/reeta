"""
==================================================
REETA — voice/speaker.py
==================================================
PURPOSE:
    Converts text to speech so REETA can "talk" to the user.
    Supports two engines:
      1. pyttsx3 — free, offline, instant (default)
      2. ElevenLabs — premium quality, online, paid (optional)

HOW pyttsx3 WORKS:
    - Uses Windows SAPI5 voices (built into Windows)
    - No internet required
    - Instant — no latency
    - Voice quality is "robotic" but perfectly clear

HOW ELEVENLABS WORKS (Phase 2 upgrade):
    - Sends text to ElevenLabs API
    - Returns high-quality, human-like audio
    - Requires API key and internet
    - Has usage limits on free tier

DESIGN DECISIONS:
    - pyttsx3 is default because it's free and instant
    - Speaker class abstracts the engine — swap engines without
      changing any other code
    - Non-blocking speech is available but not default
      (synchronous is simpler and more reliable for Phase 1)
==================================================
"""

import threading
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class Speaker:
    """
    Text-to-speech engine for REETA.

    Speaks text aloud using the configured TTS engine.
    Default is pyttsx3 (offline, free). Can be switched
    to ElevenLabs via settings.

    Usage:
        speaker = Speaker()
        speaker.speak("Hello! I am Reeta, your AI assistant.")
    """

    def __init__(self):
        """Initialize the TTS engine based on settings."""
        self.engine_name = settings.TTS_ENGINE
        self._engine = None
        self._setup_engine()

    def _setup_engine(self):
        """
        Set up the TTS engine.

        For pyttsx3:
        - Initialize the SAPI5 engine (Windows)
        - Set voice, speed, and volume
        - List available voices so user can choose

        For ElevenLabs:
        - Validate API key
        - Set up the client
        """
        if self.engine_name == "pyttsx3":
            self._setup_pyttsx3()
        elif self.engine_name == "elevenlabs":
            self._setup_elevenlabs()
        else:
            logger.warning(
                f"Unknown TTS engine: '{self.engine_name}'. Falling back to pyttsx3."
            )
            self.engine_name = "pyttsx3"
            self._setup_pyttsx3()

    def _setup_pyttsx3(self):
        """Initialize pyttsx3 (offline TTS)."""
        try:
            import pyttsx3

            self._engine = pyttsx3.init()

            # ── Configure voice properties ──────────────────
            # Speed: Words per minute (default ~200, we use 175 for clarity)
            self._engine.setProperty("rate", 175)

            # Volume: 0.0 to 1.0
            self._engine.setProperty("volume", 0.9)

            # Voice selection: Try to find a female voice for REETA
            voices = self._engine.getProperty("voices")
            voice_set = False

            if voices:
                # Log available voices for debugging
                logger.debug(f"Available TTS voices ({len(voices)}):")
                for i, voice in enumerate(voices):
                    logger.debug(f"  [{i}] {voice.name} ({voice.id})")

                # Try to find a female English voice
                for voice in voices:
                    # Windows typically has "Zira" (female) and "David" (male)
                    if "zira" in voice.name.lower() or "female" in voice.name.lower():
                        self._engine.setProperty("voice", voice.id)
                        logger.info(f"TTS voice set to: {voice.name}")
                        voice_set = True
                        break

                # If no female voice found, use the first available
                if not voice_set and voices:
                    self._engine.setProperty("voice", voices[0].id)
                    logger.info(f"TTS voice set to: {voices[0].name}")

            logger.info("pyttsx3 TTS engine initialized ✓")

        except ImportError:
            logger.error(
                "pyttsx3 not installed. Run: pip install pyttsx3"
            )
            raise
        except Exception as e:
            logger.error(f"pyttsx3 initialization failed: {e}", exc_info=True)
            raise

    def _setup_elevenlabs(self):
        """Initialize ElevenLabs TTS (premium online voice)."""
        try:
            if not settings.ELEVENLABS_API_KEY:
                logger.warning(
                    "ElevenLabs API key not set. Falling back to pyttsx3."
                )
                self.engine_name = "pyttsx3"
                self._setup_pyttsx3()
                return

            # ElevenLabs setup would go here
            # For Phase 1, we'll document the integration point
            logger.info("ElevenLabs TTS engine initialized ✓")

        except ImportError:
            logger.warning("elevenlabs package not installed. Falling back to pyttsx3.")
            self.engine_name = "pyttsx3"
            self._setup_pyttsx3()

    def speak(self, text: str) -> None:
        """
        Speak the given text aloud.

        This is SYNCHRONOUS — it blocks until speech is complete.
        Use speak_async() if you need non-blocking speech.

        Args:
            text: The text to speak aloud
        """
        if not text or not text.strip():
            logger.warning("Empty text passed to speak()")
            return

        # Clean text for speech (remove markdown, code blocks, etc.)
        clean = self._clean_for_speech(text)
        logger.info(f"🔊 Speaking: '{clean[:80]}{'...' if len(clean) > 80 else ''}'")

        try:
            if self.engine_name == "pyttsx3":
                self._speak_pyttsx3(clean)
            elif self.engine_name == "elevenlabs":
                self._speak_elevenlabs(clean)
        except Exception as e:
            logger.error(f"TTS failed: {e}", exc_info=True)
            # Fallback: just print the text
            print(f"\n💬 REETA: {clean}\n")

    def speak_async(self, text: str) -> threading.Thread:
        """
        Speak text in a background thread (non-blocking).

        Returns the thread object so the caller can wait if needed.

        Args:
            text: The text to speak

        Returns:
            Thread object running the speech
        """
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
        return thread

    def _speak_pyttsx3(self, text: str) -> None:
        """Speak using pyttsx3 engine."""
        if self._engine is None:
            logger.error("pyttsx3 engine not initialized")
            return

        # pyttsx3 needs a fresh engine per call to avoid threading issues
        # Re-create if the engine is in a bad state
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except RuntimeError:
            # Engine was likely in the middle of something
            # Re-initialize and try again
            logger.debug("Reinitializing pyttsx3 engine...")
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 175)
            self._engine.setProperty("volume", 0.9)
            self._engine.say(text)
            self._engine.runAndWait()

    def _speak_elevenlabs(self, text: str) -> None:
        """
        Speak using ElevenLabs API.

        This is a placeholder for Phase 2 integration.
        When implemented, it will:
        1. Send text to ElevenLabs API
        2. Receive audio stream
        3. Play audio using simpleaudio or pygame

        For now, falls back to pyttsx3.
        """
        logger.info("ElevenLabs TTS: Using API for premium voice")

        try:
            from elevenlabs import generate, play

            audio = generate(
                text=text,
                voice="Rachel",  # Natural female voice
                model="eleven_monolingual_v1",
                api_key=settings.ELEVENLABS_API_KEY,
            )
            play(audio)

        except ImportError:
            logger.warning("elevenlabs package not available, falling back to pyttsx3")
            self._speak_pyttsx3(text)
        except Exception as e:
            logger.warning(f"ElevenLabs failed: {e}. Falling back to pyttsx3")
            self._speak_pyttsx3(text)

    @staticmethod
    def _clean_for_speech(text: str) -> str:
        """
        Clean text to make it more natural for speech output.

        Removes things that sound weird when spoken aloud:
        - Markdown formatting (**, ##, ```)
        - URLs
        - Code blocks
        - Excessive punctuation

        Args:
            text: Raw text (potentially with markdown)

        Returns:
            Clean text suitable for speech
        """
        import re

        # Remove markdown bold/italic
        text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)

        # Remove markdown headers
        text = re.sub(r"#{1,6}\s*", "", text)

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "code block omitted", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove URLs
        text = re.sub(r"https?://\S+", "a link", text)

        # Remove bullet points
        text = re.sub(r"^[\s]*[-*•]\s*", "", text, flags=re.MULTILINE)

        # Collapse multiple newlines
        text = re.sub(r"\n{2,}", ". ", text)
        text = re.sub(r"\n", " ", text)

        # Collapse multiple spaces
        text = re.sub(r"\s{2,}", " ", text)

        return text.strip()

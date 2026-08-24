"""
==================================================
REETA — voice/listener.py
==================================================
PURPOSE:
    After the wake word is detected, this module records
    the user's actual command and transcribes it to text
    using OpenAI's Whisper model (runs locally).

HOW IT WORKS:
    1. Records audio from the microphone
    2. Saves it as a temporary WAV file
    3. Feeds it to the Whisper model for transcription
    4. Returns the transcribed text

WHY WHISPER (LOCAL) INSTEAD OF GOOGLE STT:
    - Much more accurate for full sentences
    - Works offline (no internet needed for transcription)
    - Handles accents, technical terms, and natural speech better
    - Free — no API costs, no rate limits
    - Privacy — audio never leaves your computer

WHISPER MODEL SIZES:
    - tiny   (~39M params): Fastest, least accurate
    - base   (~74M params): Good balance ← DEFAULT
    - small  (~244M params): Better accuracy, slower
    - medium (~769M params): High accuracy, needs good GPU
    - large  (~1.5B params): Best accuracy, needs powerful GPU
==================================================
"""

import tempfile
import os
import numpy as np
import speech_recognition as sr
import concurrent.futures

from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Global Whisper model — loaded once, reused for every transcription
# This avoids reloading the model for every command (would be slow)
_whisper_model = None

def _reload_whisper_model():
    """Force reload the model if it gets corrupted."""
    global _whisper_model
    _whisper_model = None
    return _load_whisper_model()

def _load_whisper_model():
    """
    Load the Whisper model into memory.

    This is called once on first use. The model stays in memory
    for fast subsequent transcriptions.

    The model downloads automatically on first run (~140MB for 'base').
    """
    global _whisper_model

    if _whisper_model is not None:
        return _whisper_model

    model_name = settings.WHISPER_MODEL
    logger.info(f"Loading Whisper model: '{model_name}' (first time may download)...")

    try:
        import whisper
        _whisper_model = whisper.load_model(model_name)
        logger.info(f"Whisper model '{model_name}' loaded successfully ✓")
        return _whisper_model
    except Exception as e:
        logger.warning(f"Whisper model unavailable ({e}). Using SpeechRecognition STT engine.")
        return None


class Listener:
    """
    Records the user's voice command and transcribes it using Whisper.

    Usage:
        listener = Listener()
        text = listener.listen_and_transcribe()
        if text:
            print(f"User said: {text}")
    """

    def __init__(self):
        """Initialize the listener with SpeechRecognition and Whisper."""
        self.recognizer = sr.Recognizer()

        # Adjust recognizer settings for command listening
        # These are tuned for clear, intentional speech (not background chatter)
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # 1 second of silence = end of phrase

        # Timeouts from settings
        self.timeout = settings.LISTEN_TIMEOUT
        self.phrase_time_limit = settings.PHRASE_TIME_LIMIT

        # Pre-load Whisper model (do it now so first command is fast)
        try:
            _load_whisper_model()
        except Exception:
            logger.warning("Whisper model failed to pre-load. Will retry on first use.")

        logger.info("Listener initialized ✓")

    def listen_and_transcribe(self) -> str:
        """
        Record audio from the microphone and transcribe it to text.

        Flow:
        1. Plays a subtle indicator that REETA is listening
        2. Records until the user stops speaking (pause detected)
        3. Transcribes the audio using Whisper
        4. Returns the cleaned text

        Returns:
            Transcribed text string, or empty string if nothing was understood

        Raises:
            No exceptions — all errors are caught and logged
        """
        logger.info("🎤 Listening for your command...")

        try:
            # Step 1: Record audio from microphone
            audio_data = self._record_audio()
            if audio_data is None:
                return ""

            # Step 2: Transcribe using Whisper (threaded with fallback)
            text = ""
            for attempt in range(3):
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(self._transcribe_with_whisper, audio_data)
                        text = future.result(timeout=15.0)  # max 15 seconds for transcription
                    break # Success
                except Exception as e:
                    logger.warning(f"Whisper transcription failed (attempt {attempt+1}/3): {e}")
                    _reload_whisper_model()

            if text:
                logger.info(f"📝 Transcribed: '{text}'")
            else:
                logger.info("No speech detected in the audio")

            return text

        except Exception as e:
            logger.error(f"Listen & transcribe failed: {e}", exc_info=True)
            return ""

    def _record_audio(self) -> sr.AudioData | None:
        """
        Capture audio from the default microphone.

        Uses SpeechRecognition to handle all the low-level audio
        capture, silence detection, and noise filtering.

        Returns:
            AudioData object, or None if recording failed
        """
        try:
            with sr.Microphone() as source:
                # Brief noise calibration (0.5 seconds)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                logger.debug(
                    f"Recording... (timeout={self.timeout}s, "
                    f"max_phrase={self.phrase_time_limit}s)"
                )

                # Record until silence is detected
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit,
                )

                logger.debug(f"Audio captured: {len(audio.get_raw_data())} bytes")
                return audio

        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout period")
            return None

        except OSError as e:
            logger.error(f"Microphone error: {e}")
            return None

    def _transcribe_with_whisper(self, audio_data: sr.AudioData) -> str:
        """
        Transcribe audio using the local Whisper model.

        Whisper expects a numpy float32 array of audio samples.
        SpeechRecognition gives us raw PCM bytes. This method
        handles the conversion.

        Args:
            audio_data: Raw audio from the microphone

        Returns:
            Transcribed text string
        """
        try:
            model = _load_whisper_model()
            if model is None:
                raise RuntimeError("Whisper model unavailable")

            # Convert SpeechRecognition AudioData → numpy array
            # Whisper expects: float32, 16kHz, mono
            raw_data = audio_data.get_raw_data(
                convert_rate=16000,     # Whisper expects 16kHz
                convert_width=2,        # 16-bit PCM
            )

            # Convert bytes → numpy float32 array (normalized to [-1, 1])
            audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
            audio_np = audio_np / 32768.0  # Normalize 16-bit to float range

            # Run Whisper transcription
            # fp16=False for CPU compatibility (GPU users can set True)
            result = model.transcribe(
                audio_np,
                language="en",       # Force English (faster, more accurate)
                fp16=False,          # Use float32 for CPU compatibility
            )

            text = result.get("text", "").strip()
            return text

        except Exception as e:
            logger.warning(f"Whisper model transcription failed ({e}). Falling back to SpeechRecognition STT...")
            try:
                text = self.recognizer.recognize_google(audio_data)
                logger.info(f"📝 Transcribed via SpeechRecognition: '{text}'")
                return text.strip()
            except Exception as fallback_err:
                logger.error(f"SpeechRecognition fallback failed: {fallback_err}")
                return ""

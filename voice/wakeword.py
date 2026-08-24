"""
==================================================
REETA — voice/wakeword.py
==================================================
PURPOSE:
    Listens passively for the wake word using openwakeword.
    Once detected, signals the main loop to start
    recording the user's actual command.

HOW IT WORKS:
    1. Uses PyAudio to capture raw microphone audio.
    2. Feeds audio chunks into openwakeword's local Model.
    3. When the confidence score crosses a threshold, returns True.
==================================================
"""

import time
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class WakeWordDetector:
    def __init__(self):
        self.enabled = settings.WAKE_WORD_ENABLED
        self.wake_word = settings.WAKE_WORD
        self.sensitivity = settings.WAKE_WORD_SENSITIVITY
        self.last_trigger_time = 0.0

        if not self.enabled:
            logger.info("Wake word detector disabled in settings.")
            return

        try:
            import numpy as np
            from openwakeword.model import Model

            logger.info("Loading openwakeword models... this may take a moment.")
            self.model = Model(inference_framework="onnx")
            self.np = np

            try:
                import pyaudio
                self.audio = pyaudio.PyAudio()
                self.mic_stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1280
                )
                self.use_pyaudio = True
            except Exception:
                import sounddevice as sd
                self.sd = sd
                self.use_pyaudio = False

            logger.info("Wake word detector initialized successfully (offline).")
            
        except ImportError as e:
            logger.error(f"Failed to import openwakeword or audio libraries ({e}). Wake word disabled.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize openwakeword: {e}")
            self.enabled = False

    def listen_for_wake_word(self) -> bool:
        """
        Listen for the wake word.
        Blocks and returns True when detected.
        """
        if not self.enabled:
            time.sleep(1) # Prevent hot loop if disabled
            return False

        if time.time() - self.last_trigger_time < 3.0:
            time.sleep(0.5)
            return False

        try:
            logger.debug("Listening for wake word...")
            
            # Read audio chunk
            if getattr(self, "use_pyaudio", True):
                pcm = self.mic_stream.read(1280, exception_on_overflow=False)
                audio = self.np.frombuffer(pcm, dtype=self.np.int16)
            else:
                rec = self.sd.rec(1280, samplerate=16000, channels=1, dtype='int16')
                self.sd.wait()
                audio = rec.flatten()
            
            # Feed to model
            prediction = self.model.predict(audio)
            
            # Check all loaded models for a trigger
            for mdl, score in prediction.items():
                if score > self.sensitivity:
                    logger.info(f"🎯 Wake word detected! (Model: {mdl}, Score: {score:.2f})")
                    self.last_trigger_time = time.time()
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Wake word detection error: {e}", exc_info=True)
            time.sleep(1)
            return False

    def calibrate(self) -> None:
        """
        Openwakeword doesn't require ambient noise calibration like SpeechRecognition.
        """
        logger.info("Calibration skipped (not required for openwakeword).")

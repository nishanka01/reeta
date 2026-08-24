"""
==================================================
REETA — config/settings.py
==================================================
PURPOSE:
    Centralized configuration for the entire REETA project.
    Loads environment variables from a .env file and exposes
    them as a clean Settings object that any module can import.

HOW IT WORKS:
    1. python-dotenv reads the .env file from the project root
    2. os.getenv() pulls each value into Python
    3. A Settings dataclass bundles everything together
    4. Other modules do: from config.settings import settings

WHY A DATACLASS:
    - Type hints make it clear what each setting is
    - IDE autocomplete works (settings.WAKE_WORD)
    - Easy to add new settings without refactoring
    - Can validate on creation
==================================================
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv


# ── Load .env file ──────────────────────────────────────────
# find_dotenv searches upward from this file to locate .env
# This ensures it works regardless of where you run the script from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


@dataclass
class Settings:
    """
    All REETA configuration in one place.
    Values come from .env file with sensible defaults.
    """

    # ── Project Paths ───────────────────────────────────────
    PROJECT_ROOT: Path = PROJECT_ROOT
    BASE_DIR: Path = PROJECT_ROOT
    LOGS_DIR: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")

    # ── LLM Configuration ──────────────────────────────────
    # Which LLM provider to use: "gemini", "anthropic", or "auto"
    # "auto" will pick whichever API key is available
    LLM_PROVIDER: str = field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "auto").lower()
    )

    # Gemini settings
    GEMINI_API_KEY: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    GEMINI_MODEL: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )

    # Anthropic (Claude) settings
    ANTHROPIC_API_KEY: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    ANTHROPIC_MODEL: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    )

    # Ollama (Free Local AI) settings
    OLLAMA_HOST: str = field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )
    OLLAMA_MODEL: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2")
    )

    # ── Live Data API Keys ──────────────────────────────────
    OPENWEATHERMAP_API_KEY: str = field(
        default_factory=lambda: os.getenv("OPENWEATHERMAP_API_KEY", "")
    )
    ALPHAVANTAGE_API_KEY: str = field(
        default_factory=lambda: os.getenv("ALPHAVANTAGE_API_KEY", "")
    )
    NEWSAPI_KEY: str = field(
        default_factory=lambda: os.getenv("NEWSAPI_KEY", "")
    )
    OPENROUTESERVICE_API_KEY: str = field(
        default_factory=lambda: os.getenv("OPENROUTESERVICE_API_KEY", "")
    )

    # ── Whisper (Speech-to-Text) ────────────────────────────
    # Model sizes: tiny, base, small, medium, large
    # Larger = more accurate but slower and uses more RAM
    WHISPER_MODEL: str = field(
        default_factory=lambda: os.getenv("WHISPER_MODEL", "base")
    )

    # ── Text-to-Speech ──────────────────────────────────────
    # Engine: "pyttsx3" (free, offline) or "elevenlabs" (premium, online)
    TTS_ENGINE: str = field(
        default_factory=lambda: os.getenv("TTS_ENGINE", "pyttsx3").lower()
    )
    ELEVENLABS_API_KEY: str = field(
        default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", "")
    )

    # ── Assistant Personality ───────────────────────────────
    WAKE_WORD: str = field(
        default_factory=lambda: os.getenv("WAKE_WORD", "hey_reeta").lower()
    )
    WAKE_WORD_ENABLED: bool = field(
        default_factory=lambda: os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
    )
    WAKE_WORD_SENSITIVITY: float = field(
        default_factory=lambda: float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
    )
    ASSISTANT_NAME: str = field(
        default_factory=lambda: os.getenv("ASSISTANT_NAME", "Reeta")
    )

    # ── System Prompt for LLM ──────────────────────────────
    SYSTEM_PROMPT: str = field(default_factory=lambda: os.getenv(
        "SYSTEM_PROMPT",
        "You are Reeta, a helpful and friendly AI desktop assistant. "
        "You run on the user's Windows computer and can help with tasks, "
        "answer questions, and have natural conversations. "
        "Keep your responses concise and conversational — you are speaking "
        "out loud, so avoid long paragraphs, code blocks, or markdown. "
        "Be warm, helpful, and to the point."
    ))

    # ── Listener Settings ───────────────────────────────────
    # How long to wait for the user to speak (seconds)
    LISTEN_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv("LISTEN_TIMEOUT", "5"))
    )
    # Maximum phrase length (seconds)
    PHRASE_TIME_LIMIT: int = field(
        default_factory=lambda: int(os.getenv("PHRASE_TIME_LIMIT", "15"))
    )

    # ── Stability Settings (Phase 3) ────────────────────────
    MAX_RETRIES: int = field(
        default_factory=lambda: int(os.getenv("MAX_RETRIES", "3"))
    )
    API_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv("API_TIMEOUT", "60"))
    )
    MEMORY_MAX_CONTEXT_ITEMS: int = field(
        default_factory=lambda: int(os.getenv("MEMORY_MAX_CONTEXT_ITEMS", "5"))
    )
    ENABLE_JSON_LOGS: bool = field(
        default_factory=lambda: os.getenv("ENABLE_JSON_LOGS", "false").lower() == "true"
    )

    def __post_init__(self):
        """Validate settings after initialization."""
        # Create logs directory if it doesn't exist
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # Determine the active LLM provider
        if self.LLM_PROVIDER == "auto":
            if self.GEMINI_API_KEY:
                self.LLM_PROVIDER = "gemini"
            elif self.ANTHROPIC_API_KEY:
                self.LLM_PROVIDER = "anthropic"
            else:
                print(
                    "\n⚠️  WARNING: No LLM API key found in .env file.\n"
                    "   REETA will work for local commands (open apps, tell time, etc.)\n"
                    "   but cannot answer general questions without an API key.\n"
                    "   Add GEMINI_API_KEY or ANTHROPIC_API_KEY to your .env file.\n"
                )
                self.LLM_PROVIDER = "none"

    def get_active_api_key(self) -> str:
        """Return the API key for the active LLM provider."""
        if self.LLM_PROVIDER == "gemini":
            return self.GEMINI_API_KEY
        elif self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_API_KEY
        return ""

    def get_active_model(self) -> str:
        """Return the model name for the active LLM provider."""
        if self.LLM_PROVIDER == "ollama":
            return self.OLLAMA_MODEL
        elif self.LLM_PROVIDER == "gemini":
            return self.GEMINI_MODEL
        elif self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_MODEL
        return ""

    def __repr__(self) -> str:
        """Pretty print settings (hides API keys for security)."""
        def mask_key(key: str) -> str:
            if not key:
                return "(not set)"
            return f"{key[:8]}...{key[-4:]}"

        return (
            f"\n{'='*50}\n"
            f"  REETA Configuration\n"
            f"{'='*50}\n"
            f"  LLM Provider:    {self.LLM_PROVIDER}\n"
            f"  Gemini Key:      {mask_key(self.GEMINI_API_KEY)}\n"
            f"  Gemini Model:    {self.GEMINI_MODEL}\n"
            f"  Anthropic Key:   {mask_key(self.ANTHROPIC_API_KEY)}\n"
            f"  Anthropic Model: {self.ANTHROPIC_MODEL}\n"
            f"  Whisper Model:   {self.WHISPER_MODEL}\n"
            f"  TTS Engine:      {self.TTS_ENGINE}\n"
            f"  Wake Word:       {self.WAKE_WORD}\n"
            f"  Assistant Name:  {self.ASSISTANT_NAME}\n"
            f"  Max Retries:     {self.MAX_RETRIES}\n"
            f"  API Timeout:     {self.API_TIMEOUT}s\n"
            f"{'='*50}\n"
        )


# ── Create the global settings instance ─────────────────────
# Every module imports this single instance:
#   from config.settings import settings
settings = Settings()

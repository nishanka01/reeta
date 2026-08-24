"""
==================================================
REETA — utils/helpers.py
==================================================
PURPOSE:
    Utility functions used across multiple REETA modules.
    Contains text processing, microphone testing, fuzzy matching,
    and system information helpers.

USAGE:
    from utils.helpers import clean_text, fuzzy_match, test_microphone
==================================================
"""

import re
import sys
import platform
from datetime import datetime


def clean_text(text: str) -> str:
    """
    Clean and normalize user input text.

    - Strips leading/trailing whitespace
    - Converts to lowercase
    - Removes extra spaces
    - Removes special characters that don't add meaning

    Args:
        text: Raw text from speech recognition

    Returns:
        Cleaned, normalized text string

    Example:
        clean_text("  Open  CHROME  please! ") → "open chrome please"
    """
    if not text:
        return ""

    # Lowercase and strip
    text = text.lower().strip()

    # Remove extra whitespace (multiple spaces → single space)
    text = re.sub(r"\s+", " ", text)

    # Remove punctuation that doesn't carry meaning in voice commands
    # Keep apostrophes (what's, don't) and hyphens (real-time)
    text = re.sub(r"[^\w\s'\-]", "", text)

    return text


def fuzzy_match(text: str, keywords: list[str], threshold: float = 0.8) -> bool:
    """
    Check if the text contains any of the keywords using flexible matching.

    This is more forgiving than exact matching — handles:
    - Partial matches ("open chrom" matches "chrome")
    - Word-level matching ("please open chrome" matches "open chrome")

    Args:
        text: The user's spoken text (already cleaned)
        keywords: List of keyword patterns to check
        threshold: Not used in Phase 1 (reserved for future fuzzy ratio matching)

    Returns:
        True if any keyword pattern is found in the text

    Example:
        fuzzy_match("open google chrome", ["open chrome", "launch chrome"]) → True
    """
    text_lower = text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()

        # Direct substring match
        if keyword_lower in text_lower:
            return True

        # Check if all words of the keyword appear in the text
        # This handles cases like "can you open chrome" matching "open chrome"
        keyword_words = keyword_lower.split()
        if all(word in text_lower for word in keyword_words):
            return True

    return False


def get_timestamp() -> str:
    """
    Get a formatted timestamp for logging and display.

    Returns:
        Formatted string like "2025-01-15 12:34:56"
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_time_spoken() -> str:
    """
    Get the current time in a natural, speakable format.

    Returns:
        String like "The current time is 3:45 PM"

    Example:
        "The current time is 12:30 PM"
    """
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")  # "03:45 PM"

    # Remove leading zero for natural speech ("3:45 PM" not "03:45 PM")
    if time_str.startswith("0"):
        time_str = time_str[1:]

    return f"The current time is {time_str}"


def get_current_date_spoken() -> str:
    """
    Get the current date in a natural, speakable format.

    Returns:
        String like "Today is Wednesday, January 15th, 2025"
    """
    now = datetime.now()

    # Get day with ordinal suffix (1st, 2nd, 3rd, 4th...)
    day = now.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    date_str = now.strftime(f"%A, %B {day}{suffix}, %Y")
    return f"Today is {date_str}"


def get_system_info() -> dict:
    """
    Gather basic system information for diagnostics.

    Returns:
        Dictionary with OS, Python version, and platform info
    """
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version.split()[0],
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def test_microphone() -> bool:
    """
    Test if the microphone is accessible and working.

    This function attempts to:
    1. Initialize PyAudio
    2. Open the default input device
    3. Record a short sample
    4. Report success or failure

    Returns:
        True if microphone works, False otherwise
    """
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()

        print("\n🎤 Testing microphone...")
        print("   Speak something in the next 3 seconds...\n")

        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)

            # Try to capture audio
            try:
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                print("   ✅ Microphone is working! Audio captured successfully.")
                print(f"   📊 Audio size: {len(audio.get_raw_data())} bytes")
                return True
            except sr.WaitTimeoutError:
                print("   ⚠️  No speech detected, but microphone IS accessible.")
                print("   This is normal if you didn't speak. Mic works fine!")
                return True

    except OSError as e:
        print(f"\n   ❌ Microphone error: {e}")
        print("   Possible fixes:")
        print("   1. Check if a microphone is connected")
        print("   2. Check Windows Sound settings → Input devices")
        print("   3. Make sure microphone permissions are enabled")
        print("   4. Try: pip install pyaudio")
        return False

    except ImportError:
        print("\n   ❌ speech_recognition not installed.")
        print("   Run: pip install SpeechRecognition PyAudio")
        return False

    except Exception as e:
        print(f"\n   ❌ Unexpected error: {e}")
        return False


def print_banner():
    """
    Print the REETA startup banner.
    Makes the console output look professional and polished.
    """
    banner = r"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██████╗ ███████╗███████╗████████╗ █████╗                   ║
    ║   ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗                 ║
    ║   ██████╔╝█████╗  █████╗     ██║   ███████║                  ║
    ║   ██╔══██╗██╔══╝  ██╔══╝     ██║   ██╔══██║                  ║
    ║   ██║  ██║███████╗███████╗   ██║   ██║  ██║                  ║
    ║   ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝                ║
    ║                                                              ║
    ║          Your AI Desktop Assistant — Phase 1                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

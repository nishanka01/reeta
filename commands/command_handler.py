"""
==================================================
REETA — commands/command_handler.py
==================================================
PURPOSE:
    Central command router — the "decision engine" of REETA.
    Receives user text, decides if it's a local command or
    an AI query, and dispatches accordingly.

HOW IT WORKS:
    1. Receives cleaned user text from the listener
    2. Checks against a keyword-based command map
    3. If matched → executes the local command via AppController
    4. If not matched → forwards to LLM brain for AI response
    5. Returns the response text to be spoken

DESIGN:
    Commands are stored as a list of (keywords, handler) tuples.
    Adding a new command = adding one entry to the list.
    No if/elif chains, no complex parsing.
==================================================
"""

from utils.logger import get_logger
from utils.helpers import clean_text, get_current_time_spoken, get_current_date_spoken
from commands.automation_router import AutomationRouter
from brain.llm_handler import LLMHandler

logger = get_logger(__name__)


class CommandHandler:
    """
    Routes user commands to the appropriate handler.

    Local commands (open apps, tell time, etc.) are handled directly.
    Everything else is forwarded to the LLM brain.
    """

    def __init__(self, brain: LLMHandler, app_controller=None):
        """
        Initialize with references to the brain and automation router.

        Args:
            brain: LLM handler for AI queries
            app_controller: Optional AppController instance
        """
        self.brain = brain
        self.app_controller = app_controller
        self.automation_router = AutomationRouter(brain)

        # ── Command Registry ────────────────────────────────
        # Reduced to only exit and utility commands
        self._commands = [
            # === Exit Commands ===
            (["exit", "quit", "stop", "goodbye", "shut down reeta",
              "bye", "go to sleep"], self._handle_exit),

            # === Utility Commands ===
            (["what time", "current time", "tell me the time", "what's the time"],
             lambda t: get_current_time_spoken()),

            (["what date", "today's date", "what day", "current date"],
             lambda t: get_current_date_spoken()),
        ]

        logger.info(
            f"Command handler initialized with {len(self._commands)} basic commands ✓"
        )

    def process(self, user_text: str) -> tuple[str, bool]:
        """
        Process user text and return the appropriate response.

        Args:
            user_text: Raw text from speech recognition

        Returns:
            Tuple of (response_text, should_exit)
            - response_text: What REETA should say back
            - should_exit: True if the user wants to quit
        """
        if not user_text or not user_text.strip():
            return "I didn't catch that. Could you say it again?", False

        # Clean the input text
        cleaned = clean_text(user_text)
        logger.info(f"Processing command: '{cleaned}'")

        # Check against command registry
        for keywords, handler in self._commands:
            if self._matches(cleaned, keywords):
                logger.info(f"Matched command: {keywords[0]}")
                result = handler(cleaned)

                # Check if it's an exit command
                if result == "__EXIT__":
                    return "Goodbye! Have a great day.", True

                return result, False

        # Route to Automation Engine if it looks like an action
        if self.automation_router.is_automation_command(cleaned):
            return self.automation_router.process(cleaned), False

        # No local command matched → forward to AI brain
        logger.info("No local command matched. Forwarding to AI brain...")
        response = self.brain.think(user_text)
        return response, False

    def _matches(self, text: str, keywords: list[str]) -> bool:
        """
        Check if text matches any of the keywords.

        Uses flexible matching:
        - Substring match ("open chrome" in "please open chrome")
        - All-words match ("open" and "chrome" both in text)
        """
        for keyword in keywords:
            kw_lower = keyword.lower()
            # Direct substring match
            if kw_lower in text:
                return True
            # All words present
            kw_words = kw_lower.split()
            if len(kw_words) > 1 and all(w in text for w in kw_words):
                return True
        return False

    def _handle_exit(self, text: str) -> str:
        """Handle exit/quit commands."""
        logger.info("Exit command received")
        return "__EXIT__"

    def _handle_exit(self, text: str) -> str:
        """Handle exit/quit commands."""
        logger.info("Exit command received")
        return "__EXIT__"

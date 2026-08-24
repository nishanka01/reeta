"""
==================================================
REETA — brain/llm_handler.py
==================================================
PURPOSE:
    REETA's "brain" — sends user queries to an LLM
    (Google Gemini or Anthropic Claude) and returns
    intelligent, conversational responses.

HOW IT WORKS:
    1. Takes the user's text input
    2. Wraps it with a system prompt that defines REETA's personality
    3. Sends it to the configured LLM API
    4. Returns the AI's response as text

SUPPORTED PROVIDERS:
    - Google Gemini (gemini-1.5-flash, gemini-1.5-pro, etc.)
    - Anthropic Claude (Claude Sonnet, etc.)
    - Auto-detection: uses whichever API key is available

ARCHITECTURE FOR PHASE 2:
    - conversation_history list is ready for memory integration
    - Just append user/assistant messages to maintain context
    - Can be extended with RAG (retrieval-augmented generation)
    - Can add multiple specialized agents (coding, research, etc.)
==================================================
"""

from utils.logger import get_logger
from config.settings import settings
from utils.retry import with_retry
from brain.tools import AVAILABLE_TOOLS

logger = get_logger(__name__)


class LLMHandler:
    """
    Manages communication with LLM APIs (Google Gemini / Anthropic).

    Handles:
    - API client initialization
    - Message formatting
    - Error handling and retries
    - Response parsing

    Usage:
        brain = LLMHandler()
        response = brain.think("What is the capital of France?")
        print(response)  # "The capital of France is Paris!"
    """

    def __init__(self):
        """
        Initialize the LLM handler based on configured provider.

        Reads the provider and API key from settings, then sets up
        the appropriate API client.
        """
        self.provider = settings.LLM_PROVIDER
        self.model = settings.get_active_model()
        self.system_prompt = settings.SYSTEM_PROMPT

        # Conversation history for context (Phase 2: persistent memory)
        # Each entry is a dict: {"role": "user"/"assistant", "content": "..."}
        self.conversation_history: list[dict] = []

        # Maximum history length to send with each request
        # Prevents token overflow and keeps costs down
        self.max_history_length = 10

        # Initialize the appropriate API client
        self._client = None
        self._setup_client()

        # Phase 2: Initialize Memory System
        try:
            from memory.memory_manager import MemoryManager
            self.memory_manager = MemoryManager(self)
        except Exception as e:
            self.memory_manager = None
            logger.warning(f"Memory System not initialized: {e}")

    def _setup_client(self):
        """
        Set up the API client for the configured provider.

        Each provider has its own SDK or REST API:
        - Ollama: Local HTTP API (http://localhost:11434)
        - Gemini: `google-genai` package
        - Anthropic: `anthropic` package
        """
        if self.provider == "ollama":
            self._setup_ollama()
        elif self.provider == "gemini":
            self._setup_gemini()
        elif self.provider == "anthropic":
            self._setup_anthropic()
        elif self.provider == "none":
            logger.warning(
                "No LLM provider configured. "
                "REETA will only handle local commands."
            )
        else:
            logger.error(f"Unknown LLM provider: '{self.provider}'")

    def _setup_ollama(self):
        """Initialize and verify the local Ollama API endpoint."""
        import requests
        try:
            res = requests.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=5)
            if res.status_code == 200:
                logger.info(f"Ollama local AI initialized (host: {settings.OLLAMA_HOST}, model: {self.model}) ✓")
            else:
                logger.warning(f"Ollama service reachable but returned status {res.status_code}")
        except Exception as e:
            logger.error(f"Ollama connection check failed at {settings.OLLAMA_HOST}: {e}")
            logger.warning("Ensure Ollama is running (`ollama serve` or system tray icon active).")

    def _setup_gemini(self):
        """Initialize the Google Gemini API client using the new google-genai SDK."""
        try:
            from google import genai

            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info(f"Gemini client initialized (model: {self.model}) ✓")

        except ImportError:
            logger.error("google-genai package not installed. Run: pip install google-genai")
            self.provider = "none"
        except Exception as e:
            logger.error(f"Gemini setup failed: {e}", exc_info=True)
            self.provider = "none"

    def _setup_anthropic(self):
        """Initialize the Anthropic (Claude) API client."""
        try:
            import anthropic

            self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info(f"Anthropic client initialized (model: {self.model}) ✓")

        except ImportError:
            logger.error("anthropic package not installed. Run: pip install anthropic")
            self.provider = "none"
        except Exception as e:
            logger.error(f"Anthropic setup failed: {e}", exc_info=True)
            self.provider = "none"

    def think(self, user_input: str) -> str:
        """
        Send the user's query to the LLM and get a response.

        This is the main method other modules call.

        Args:
            user_input: The user's text query

        Returns:
            The AI's response as a string.
            Returns a fallback message if the API fails.
        """
        if self.provider == "none":
            return (
                "I'm sorry, I can't answer that question right now. "
                "I don't have an AI brain connected. "
                "Please add a Gemini or Anthropic API key to the .env file."
            )

        if not user_input or not user_input.strip():
            return "I didn't catch that. Could you say it again?"

        logger.info(f"🧠 Thinking about: '{user_input[:80]}...'")

        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
            })

            # Phase 2: Retrieve context
            current_system_prompt = self.system_prompt
            if self.memory_manager:
                # Add User Profile to system prompt
                user_profile = self.memory_manager.get_user_profile()
                if user_profile:
                    profile_str = "\n".join(f"- {k}: {v}" for k, v in user_profile.items())
                    current_system_prompt += f"\n\nUser Profile:\n{profile_str}"

                memories = self.memory_manager.get_relevant_context(user_input)
                from brain.context_builder import ContextBuilder
                current_system_prompt = ContextBuilder.build_system_prompt_with_context(
                    current_system_prompt, memories
                )
                
                # Asynchronously process and store the interaction
                self.memory_manager.process_interaction_async(user_input)
                
                # Log conversation to SQLite
                self.memory_manager.log_conversation("user", user_input)

            # Get response from the appropriate provider
            if self.provider == "ollama":
                response = self._query_ollama(user_input, current_system_prompt)
            elif self.provider == "gemini":
                response = self._query_gemini(user_input, current_system_prompt)
            elif self.provider == "anthropic":
                response = self._query_anthropic(user_input, current_system_prompt)
            else:
                response = "I'm having trouble connecting to my brain right now."

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
            })
            if self.memory_manager:
                self.memory_manager.log_conversation("assistant", response)

            # Trim history to prevent token overflow
            if len(self.conversation_history) > self.max_history_length * 2:
                self.conversation_history = self.conversation_history[
                    -(self.max_history_length * 2):
                ]

            logger.info(
                f"💡 Response: '{response[:80]}{'...' if len(response) > 80 else ''}'"
            )
            return response

        except Exception as e:
            logger.error(f"LLM query failed after retries: {e}", exc_info=True)
            return (
                "I'm sorry, I encountered an error while thinking about that. "
                "My connection might be unstable. Please try again."
            )

    @with_retry(max_retries=settings.MAX_RETRIES, base_delay=1.0)
    def _query_ollama(self, user_input: str, system_prompt: str = None) -> str:
        """
        Send a query to local Ollama API server.

        Args:
            user_input: The user's query
            system_prompt: Optional override for the system prompt

        Returns:
            The AI's response text
        """
        import requests

        prompt_to_use = system_prompt if system_prompt else self.system_prompt
        messages = [{"role": "system", "content": prompt_to_use}]

        # Add recent conversation history
        recent_history = self.conversation_history[-(self.max_history_length * 2):]
        if recent_history and recent_history[-1]["role"] == "user":
            recent_history = recent_history[:-1]

        messages.extend(recent_history)
        messages.append({"role": "user", "content": user_input})

        try:
            res = requests.post(
                f"{settings.OLLAMA_HOST}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                },
                timeout=settings.API_TIMEOUT
            )
            if res.status_code == 200:
                data = res.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                logger.error(f"Ollama returned error {res.status_code}: {res.text}")
                return "Local AI service encountered an error."
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise

    @with_retry(max_retries=settings.MAX_RETRIES, base_delay=1.0)
    def _query_gemini(self, user_input: str, system_prompt: str = None) -> str:
        """
        Send a query to Google Gemini's API using the google-genai SDK.

        Uses the generate_content endpoint with:
        - System instruction (REETA's personality)
        - Recent conversation history (for context)
        - Current user message

        Args:
            user_input: The user's query
            system_prompt: Optional override for the system prompt

        Returns:
            The AI's response text
        """
        from google import genai
        from google.genai import types

        try:
            # Build the contents array for Gemini
            prompt_to_use = system_prompt if system_prompt else self.system_prompt

            # Build conversation history as Content objects
            contents = []

            # Add recent conversation history for context
            recent_history = self.conversation_history[-(self.max_history_length * 2):]
            # Don't include the last user message (it's already in the history
            # but we want to add it explicitly below)
            if recent_history and recent_history[-1]["role"] == "user":
                recent_history = recent_history[:-1]

            for msg in recent_history:
                # Gemini uses "user" and "model" roles (not "assistant")
                role = "model" if msg["role"] == "assistant" else msg["role"]
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            # Add the current user message
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_input)]
                )
            )

            # Configure generation parameters
            # Note: We rely on the genai client's default timeout or wrapped timeout handling
            generate_config = types.GenerateContentConfig(
                system_instruction=prompt_to_use,
                max_output_tokens=300,       # Keep responses concise (spoken output)
                temperature=0.7,             # Balanced creativity/accuracy
                top_p=0.9,
                tools=AVAILABLE_TOOLS,       # Enable Live Data function calling
            )

            # Call the API
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_config,
            )

            # Check if the model decided to call a tool
            if response.function_calls:
                # For simplicity and speed in a voice assistant, we execute the tool
                # and return its pre-formatted string directly, saving an LLM roundtrip.
                function_call = response.function_calls[0]
                func_name = function_call.name
                func = next((f for f in AVAILABLE_TOOLS if f.__name__ == func_name), None)
                
                if func:
                    args = {k: v for k, v in function_call.args.items()} if function_call.args else {}
                    logger.info(f"Executing tool: {func_name} with args {args}")
                    tool_result = func(**args)
                    return str(tool_result)
                else:
                    return f"I tried to use a tool called {func_name} but couldn't find it."

            return response.text.strip()

        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "resource_exhausted" in error_msg:
                logger.warning(f"Gemini rate limit hit: {e}")
                return "I'm being rate limited. Please wait a moment and try again."
            elif "403" in error_msg or "401" in error_msg or "permission" in error_msg:
                logger.error(f"Gemini auth error: {e}")
                return "I had trouble connecting to my brain. Check your API key."
            elif "timeout" in error_msg:
                logger.warning("Gemini API timeout.")
                raise  # Let the retry decorator handle timeouts
            else:
                logger.error(f"Gemini query failed, triggering retry if possible: {e}")
                raise

    @with_retry(max_retries=settings.MAX_RETRIES, base_delay=1.0)
    def _query_anthropic(self, user_input: str, system_prompt: str = None) -> str:
        """
        Send a query to Anthropic's Claude API.

        Claude's API is slightly different from Gemini's:
        - System prompt is a separate parameter (not in messages)
        - Messages array only contains user/assistant messages
        - Response format is different

        Args:
            user_input: The user's query

        Returns:
            The AI's response text
        """
        import anthropic

        try:
            # Build messages (Claude doesn't put system prompt in messages)
            messages = []

            # Add recent conversation history
            recent_history = self.conversation_history[-(self.max_history_length * 2):]
            if recent_history and recent_history[-1]["role"] == "user":
                recent_history = recent_history[:-1]

            messages.extend(recent_history)

            # Add current user message
            messages.append({"role": "user", "content": user_input})

            # Define tools for Claude
            claude_tools = [
                {
                    "name": "get_weather",
                    "description": "Get the current weather for a specific city or location.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "The name of the city (e.g., 'London', 'New York')."}
                        },
                        "required": ["location"]
                    }
                },
                {
                    "name": "get_stock_price",
                    "description": "Get the current stock price for a given ticker symbol.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL', 'MSFT')."}
                        },
                        "required": ["ticker"]
                    }
                },
                {
                    "name": "get_news",
                    "description": "Get the latest top news headlines, optionally for a specific topic.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "The topic to search for (e.g., 'technology', 'sports', 'general')."}
                        }
                    }
                },
                {
                    "name": "get_route",
                    "description": "Get driving directions or route information between two locations.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "The starting location."},
                            "destination": {"type": "string", "description": "The destination location."}
                        },
                        "required": ["origin", "destination"]
                    }
                }
            ]

            # Call the API
            prompt_to_use = system_prompt if system_prompt else self.system_prompt
            response = self._client.messages.create(
                model=self.model,
                system=prompt_to_use,  # Claude takes system prompt separately
                messages=messages,
                tools=claude_tools,
                max_tokens=300,
                temperature=0.7,
                timeout=settings.API_TIMEOUT,
            )

            # Check for tool use
            if response.stop_reason == "tool_use":
                for block in response.content:
                    if block.type == "tool_use":
                        func_name = block.name
                        func = next((f for f in AVAILABLE_TOOLS if f.__name__ == func_name), None)
                        if func:
                            logger.info(f"Executing tool: {func_name} with args {block.input}")
                            tool_result = func(**block.input)
                            return str(tool_result)
                        return f"I tried to use a tool called {func_name} but couldn't find it."

            # Claude returns content as a list of content blocks
            return response.content[0].text.strip()

        except anthropic.APITimeoutError:
            logger.warning("Claude API timeout.")
            raise  # Handled by retry decorator
        except anthropic.RateLimitError:
            logger.warning("Claude rate limit hit.")
            raise  # Handled by retry decorator
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise  # Handled by retry decorator
        except Exception as e:
            logger.error(f"Claude query failed: {e}", exc_info=True)
            raise

    def clear_history(self):
        """
        Clear the conversation history.

        Useful for:
        - Starting a fresh conversation
        - Reducing token usage
        - Privacy (clearing sensitive queries)
        """
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

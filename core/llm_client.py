"""
==================================================
REETA — core/llm_client.py
==================================================
PURPOSE:
    Provides a centralized, resilient client for LLM API calls.
    Includes exponential backoff for rate limits and timeouts.
==================================================
"""

from tenacity import retry, stop_after_attempt, wait_exponential
from utils.logger import get_logger
import asyncio

logger = get_logger("core.llm_client")

class LLMClient:
    def __init__(self):
        # Setup mock/real client here
        pass

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_response(self, prompt: str) -> str:
        """
        Synchronous generation with exponential backoff.
        Useful for planning and basic agent tasks.
        """
        logger.info("Sending prompt to LLM (with retry backoff)...")
        # MOCK LLM CALL
        # In production, replace with actual openai.ChatCompletion.create or gemini call
        if "fail" in prompt.lower():
            raise Exception("Simulated rate limit / network failure")
        return f"LLM Response to: {prompt}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    async def generate_response_async(self, prompt: str) -> str:
        """
        Asynchronous generation to prevent blocking the event loop.
        """
        logger.info("Sending async prompt to LLM...")
        await asyncio.sleep(0.5) # Simulate network IO
        if "fail" in prompt.lower():
            raise Exception("Simulated rate limit / network failure")
        return f"Async LLM Response to: {prompt}"

# Singleton instance
llm_client = LLMClient()

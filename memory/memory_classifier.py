"""
==================================================
REETA — memory/memory_classifier.py
==================================================
PURPOSE:
    Analyzes the user's input to determine if it should be saved
    to long-term memory. Extracts facts and assigns a category.
==================================================
"""

import json
from utils.logger import get_logger
from config.settings import settings
from memory.memory_models import ClassificationResult

logger = get_logger(__name__)

class MemoryClassifier:
    """
    Uses the AI brain (LLM) to classify inputs as memorable or not.
    """
    
    def __init__(self, brain):
        # We take an instance of LLMHandler
        self.brain = brain
        
        self.classifier_prompt = (
            "You are a Memory Classification AI for an assistant named REETA.\n"
            "Analyze the following user input and decide if it contains information "
            "that REETA should remember for the future (e.g., a preference, a project detail, "
            "a personal fact, or a task).\n"
            "Output your analysis strictly in JSON format with three keys:\n"
            "- \"should_remember\": boolean (true if worth remembering, false otherwise)\n"
            "- \"category\": string (one of: 'preference', 'project', 'task', 'personal_fact', 'none')\n"
            "- \"extracted_fact\": string (a clear, standalone sentence describing what to remember. "
            "Make it objective, e.g., 'The user is building an AI called REETA' or 'The user's favorite language is Python'. "
            "Leave empty if should_remember is false.)\n"
            "\n"
            "Output ONLY valid JSON. No other text."
        )

    def classify(self, user_input: str) -> ClassificationResult:
        """
        Asks the LLM to classify the input.
        Returns a ClassificationResult.
        """
        default_result = ClassificationResult(
            should_remember=False, 
            category="none", 
            extracted_fact=""
        )
        
        if not user_input or self.brain.provider == "none":
            return default_result

        try:
            # We bypass the normal conversation history and system prompt of the brain
            # by directly calling the underlying API methods, or by temporarily swapping the prompt.
            # For robustness, we'll construct a direct prompt here.
            
            prompt = f"{self.classifier_prompt}\n\nUser Input: \"{user_input}\""
            
            # Since LLMHandler keeps state, we will temporarily save its history
            # and restore it to prevent polluting the chat memory with classification logic.
            original_history = self.brain.conversation_history.copy()
            original_prompt = self.brain.system_prompt
            
            self.brain.conversation_history = []
            self.brain.system_prompt = prompt
            
            # Use the brain to get the classification
            try:
                if self.brain.provider == "gemini":
                    response_text = self.brain._query_gemini(user_input)
                elif self.brain.provider == "anthropic":
                    response_text = self.brain._query_anthropic(user_input)
                elif self.brain.provider == "ollama":
                    response_text = self.brain._query_ollama(user_input)
                else:
                    logger.error(f"Unknown provider for classification: {self.brain.provider}")
                    return default_result
            finally:
                # Restore state guaranteed
                self.brain.conversation_history = original_history
                self.brain.system_prompt = original_prompt

            # Parse JSON
            # Sometimes LLMs wrap JSON in markdown block (```json ... ```)
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(cleaned)
            
            result = ClassificationResult(
                should_remember=data.get("should_remember", False),
                category=data.get("category", "none"),
                extracted_fact=data.get("extracted_fact", "")
            )
            
            if result.should_remember:
                logger.info(f"Memory detected: [{result.category}] {result.extracted_fact}")
            
            return result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse classification JSON from LLM")
            return default_result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return default_result

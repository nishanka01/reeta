"""
==================================================
REETA — brain/context_builder.py
==================================================
PURPOSE:
    Takes raw memory facts retrieved from the vector store
    and formats them perfectly to be injected into the LLM's
    system prompt.
==================================================
"""

from typing import List

class ContextBuilder:
    """
    Formats memories for context injection.
    """
    
    @staticmethod
    def build_system_prompt_with_context(base_prompt: str, memories: List[str]) -> str:
        """
        Appends relevant memories to the base system prompt.
        """
        if not memories:
            return base_prompt
            
        context_section = "\n\n--- RELEVANT MEMORIES (Context for current query) ---\n"
        context_section += "You remember the following facts from past conversations:\n"
        
        for idx, memory in enumerate(memories, 1):
            context_section += f"{idx}. {memory}\n"
            
        context_section += "Use this context to inform your response if it is relevant to the user's query."
        
        return base_prompt + context_section

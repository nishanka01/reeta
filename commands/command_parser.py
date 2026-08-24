"""
==================================================
REETA — commands/command_parser.py
==================================================
PURPOSE:
    Uses the LLM to parse complex natural language into
    a structured JSON array of discrete automation steps.
==================================================
"""

import json
from utils.logger import get_logger
from brain.llm_handler import LLMHandler

logger = get_logger(__name__)

class CommandParser:
    """Extracts structured intent from raw text."""

    def __init__(self, llm_handler: LLMHandler):
        self.llm = llm_handler

    def parse_workflow(self, user_text: str) -> list[dict]:
        """
        Converts text like "Open chrome and search cats"
        into: [{"action": "open_app", "target": "chrome"}, {"action": "web_search", "target": "cats"}]
        """
        prompt = f"""
        You are an automation intent parser.
        Extract the sequence of actions from the user's request.
        
        Available actions:
        - open_app (target: app name)
        - close_app (target: app name)
        - web_search (target: search query)
        - open_url (target: website name or url)
        - create_folder (target: folder name)
        - delete_file (target: file path)
        - type_text (target: text to type)
        - press_key (target: shortcut like 'ctrl+c')
        - add_calendar_event (target: JSON string {{"title": "...", "datetime": "YYYY-MM-DD HH:MM"}})
        - read_reminders (target: "")
        - send_message (target: JSON string {{"platform": "email", "contact": "...", "text": "..."}})
        - scan_document (target: file path)

        User request: "{user_text}"
        
        Respond ONLY with a valid JSON array of objects.
        Example: [ {{"action": "open_app", "target": "chrome"}} ]
        """
        
        try:
            logger.info("Parsing workflow intent...")
            # We bypass memory for raw parsing
            response_text = self.llm.client.models.generate_content(
                model=self.llm.model_name,
                contents=prompt
            ).text

            # Clean JSON markdown blocks if present
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            
            steps = json.loads(cleaned)
            if isinstance(steps, list):
                logger.debug(f"Parsed {len(steps)} steps: {steps}")
                return steps
            return []
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM: {response_text}")
            return []
        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            return []

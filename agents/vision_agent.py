"""
==================================================
REETA — agents/vision_agent.py
==================================================
PURPOSE:
    Orchestrates the computer vision pipelines. Captures the screen,
    runs OCR, performs UI detection, and feeds the formatted multimodal
    context back into the LangGraph state.
==================================================
"""

from agents.base_agent import BaseAgent
from vision.screen_capture import screen_capturer
from vision.ocr_engine import ocr_engine
from multimodal.vision_context_manager import vision_context

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="VisionAgent", description="Analyzes screen content, reads text, and identifies UI elements.")

    def run(self, state: dict) -> dict:
        self.log_action("Executing vision analysis task.")
        try:
            # 1. Capture the screen
            self.log_action("Capturing screen...")
            img_bgr = screen_capturer.capture_full_screen(save_to_disk=True)
            
            if img_bgr is None:
                raise Exception("Failed to capture screen image.")

            # 2. Run OCR
            self.log_action("Running OCR text extraction...")
            raw_text = ocr_engine.extract_text(img_bgr)
            
            # 3. Format Multimodal Context
            formatted_context = vision_context.format_screen_context(raw_text)
            
            # 4. Update the Task Plan status
            task_plan = state.get("task_plan", [])
            for step in task_plan:
                if step.get("agent") == self.name and step.get("status") == "pending":
                    step["status"] = "completed"
                    break

            # 5. Return updated state
            self.log_action("Vision analysis complete.")
            return {
                "current_agent": self.name,
                "task_plan": task_plan,
                "shared_context": {"vision_analysis": formatted_context},
                "messages": [{"role": "system", "content": "VisionAgent extracted screen context successfully."}]
            }
            
        except Exception as e:
            return self.error_recovery(e)

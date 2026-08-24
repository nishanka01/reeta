"""
==================================================
REETA — agents/security_agent.py
==================================================
PURPOSE:
    Handles phishing detection, suspicious URL analysis, and security.
==================================================
"""

from agents.base_agent import BaseAgent
from security.url_analyzer import url_analyzer
from security.phishing_detector import phishing_detector
from security.file_scanner import file_scanner
from security.threat_intelligence import threat_intel
from security.risk_scoring import risk_scorer

class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SecurityAgent", description="Analyzes cybersecurity risks.")

    def run(self, state: dict) -> dict:
        self.log_action("Executing security analysis task.")
        try:
            # Check what needs to be analyzed (mock routing logic for now)
            user_request = state.get("user_request", "").lower()
            shared_context = state.get("shared_context", {})
            
            risk_report = None
            
            # Example 1: URL Analysis
            if "url" in user_request or "http" in user_request:
                # Extract URL from request (naive extraction for demo)
                words = user_request.split()
                url = next((w for w in words if "http" in w or ".com" in w), "http://unknown.com")
                
                # Run pipelines
                phishing_data = phishing_detector.analyze_webpage(url, visual_context=shared_context.get("vision_analysis"))
                domain = url_analyzer.parse_url(url).get("domain")
                intel_data = threat_intel.lookup_domain(domain) if domain else {}
                
                risk_report = risk_scorer.aggregate_url_risk(phishing_data, intel_data)
                self.log_action(f"Analyzed URL {url} - Severity: {risk_report['severity']}")

            # Example 2: File Analysis
            elif "file" in user_request or "download" in user_request:
                # We'd typically get the filepath from the automation agent, use dummy path
                filepath = "dummy_file.exe" 
                
                # Run pipelines
                scanner_data = file_scanner.analyze_file(filepath)
                intel_data = threat_intel.lookup_hash(scanner_data.get("sha256")) if scanner_data.get("sha256") else {}
                
                risk_report = risk_scorer.aggregate_file_risk(scanner_data, intel_data)
                self.log_action(f"Analyzed File {filepath} - Severity: {risk_report['severity']}")

            # Finish task step
            task_plan = state.get("task_plan", [])
            for step in task_plan:
                if step.get("agent") == self.name and step.get("status") == "pending":
                    step["status"] = "completed"
                    break

            return {
                "current_agent": self.name,
                "task_plan": task_plan,
                "shared_context": {"security_risk_report": risk_report},
                "messages": [{"role": "system", "content": f"SecurityAgent completed risk analysis. Result: {risk_report}"}]
            }
        except Exception as e:
            return self.error_recovery(e)

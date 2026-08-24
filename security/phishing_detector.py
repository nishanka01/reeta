"""
==================================================
REETA — security/phishing_detector.py
==================================================
PURPOSE:
    Aggregates URL analysis and visual context (from Vision System)
    to generate a phishing probability score.
==================================================
"""

from security.url_analyzer import url_analyzer
from utils.logger import get_logger

logger = get_logger("security.phishing")

class PhishingDetector:
    def __init__(self):
        pass

    def analyze_webpage(self, url: str, visual_context: str = None) -> dict:
        """
        Combines URL heuristics with visual clues to detect phishing.
        """
        logger.info(f"Analyzing webpage for phishing: {url}")
        
        url_data = url_analyzer.parse_url(url)
        if not url_data:
            return {"risk_score": 0, "reason": "Invalid URL format."}

        domain = url_data.get("domain")
        typo_check = url_analyzer.check_typosquatting(domain)
        
        risk_score = 0
        reasons = []

        # 1. Typo-squatting penalty
        if typo_check["is_typosquat"]:
            risk_score += 60
            reasons.append(f"Domain '{domain}' is likely typo-squatting '{typo_check['target']}'.")

        # 2. Suspicious TLD penalty
        suspicious_tlds = ["xyz", "top", "tk", "ml", "ga", "cf", "gq"]
        if url_data.get("suffix") in suspicious_tlds:
            risk_score += 30
            reasons.append(f"Domain uses a frequently abused TLD (.{url_data.get('suffix')}).")

        # 3. Overly long subdomains (often used to obscure the real domain)
        subdomain = url_data.get("subdomain", "")
        if len(subdomain.split(".")) > 3:
            risk_score += 20
            reasons.append("URL contains an unusually high number of subdomains.")

        # 4. Visual Context matching (Multimodal integration)
        # If the vision system sees a Microsoft login box, but the domain isn't microsoft.com
        if visual_context:
            visual_lower = visual_context.lower()
            if "microsoft" in visual_lower or "sign in" in visual_lower:
                if domain != "microsoft" and domain != "live":
                    risk_score += 80
                    reasons.append("Visual mismatch: Page looks like a Microsoft login but the domain does not match.")

        # Cap score at 100
        risk_score = min(risk_score, 100)
        
        return {
            "url": url,
            "phishing_probability": risk_score,
            "is_phishing": risk_score > 60,
            "indicators": reasons
        }

# Singleton instance
phishing_detector = PhishingDetector()

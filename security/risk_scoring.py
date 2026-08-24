"""
==================================================
REETA — security/risk_scoring.py
==================================================
PURPOSE:
    Aggregates data from all security modules into a single
    standardized risk score and severity label.
==================================================
"""

class RiskScoring:
    def __init__(self):
        pass

    def get_severity_label(self, score: int) -> str:
        if score >= 80:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        else:
            return "LOW"

    def aggregate_url_risk(self, phishing_data: dict, intel_data: dict) -> dict:
        """
        Combines local heuristics with cloud threat intelligence.
        """
        base_score = phishing_data.get("phishing_probability", 0)
        indicators = phishing_data.get("indicators", [])

        # If threat intel says it's definitely bad, jump to max risk
        if intel_data.get("is_malicious"):
            base_score = 100
            indicators.append(f"Blacklisted by Threat Intel: {intel_data.get('details', {}).get('classification')}")

        final_score = min(base_score, 100)
        
        return {
            "score": final_score,
            "severity": self.get_severity_label(final_score),
            "indicators": indicators
        }
        
    def aggregate_file_risk(self, scanner_data: dict, intel_data: dict) -> dict:
        base_score = scanner_data.get("risk_score", 0)
        indicators = scanner_data.get("indicators", [])

        if intel_data.get("is_malicious"):
            base_score = 100
            indicators.append(f"Hash blacklisted by Threat Intel: {intel_data.get('details', {}).get('classification')}")

        final_score = min(base_score, 100)
        
        return {
            "score": final_score,
            "severity": self.get_severity_label(final_score),
            "indicators": indicators
        }

# Singleton instance
risk_scorer = RiskScoring()

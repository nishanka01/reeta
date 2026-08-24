"""
==================================================
REETA — security/threat_intelligence.py
==================================================
PURPOSE:
    Interfaces with external reputation databases.
    (Currently uses mock data to simulate an API like VirusTotal).
==================================================
"""

from functools import lru_cache
from utils.logger import get_logger

logger = get_logger("security.threat_intel")

class ThreatIntelligence:
    def __init__(self):
        # In a real scenario, this would load an API key from .env
        pass

    @lru_cache(maxsize=500)
    def lookup_hash(self, file_hash: str) -> dict:
        """
        Queries a mock reputation database for a file hash.
        Cached to prevent hammering the external API.
        """
        logger.info(f"Looking up hash reputation: {file_hash}")
        
        # Mock database of known bad hashes
        known_malware = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
                "classification": "Trojan.Win32.Generic",
                "malicious_votes": 45,
                "total_votes": 60
            }
        }
        
        if file_hash in known_malware:
            data = known_malware[file_hash]
            return {
                "found": True,
                "is_malicious": True,
                "details": data
            }
            
        return {"found": False, "is_malicious": False}

    @lru_cache(maxsize=500)
    def lookup_domain(self, domain: str) -> dict:
        """
        Queries a mock reputation database for a domain.
        Cached to prevent hammering the external API.
        """
        logger.info(f"Looking up domain reputation: {domain}")
        
        known_phishing = ["g00gle.com", "micros0ft.com", "secure-login-paypal.com"]
        
        if domain in known_phishing:
            return {
                "found": True,
                "is_malicious": True,
                "details": {"classification": "Phishing/Fraud"}
            }
            
        return {"found": False, "is_malicious": False}

# Singleton instance
threat_intel = ThreatIntelligence()

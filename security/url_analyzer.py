"""
==================================================
REETA — security/url_analyzer.py
==================================================
PURPOSE:
    Parses URLs safely, extracts domain components, and
    detects basic typo-squatting against known brands.
==================================================
"""

import tldextract
from functools import lru_cache
from utils.logger import get_logger

logger = get_logger("security.url")

# Known high-value targets often typo-squatted
KNOWN_BRANDS = ["google", "microsoft", "apple", "amazon", "facebook", "paypal", "netflix"]

class URLAnalyzer:
    def __init__(self):
        pass

    @lru_cache(maxsize=1000)
    def parse_url(self, url: str) -> dict:
        """
        Extracts subdomains, domain, and suffix (TLD) accurately.
        Cached to prevent redundant parsing of the same URLs.
        """
        try:
            # tldextract handles complex TLDs like .co.uk natively
            ext = tldextract.extract(url)
            return {
                "url": url,
                "subdomain": ext.subdomain,
                "domain": ext.domain,
                "suffix": ext.suffix,
                "registered_domain": ext.registered_domain
            }
        except Exception as e:
            logger.error(f"Failed to parse URL {url}: {str(e)}")
            return {}

    def check_typosquatting(self, domain: str) -> dict:
        """
        Simple heuristic: check if the domain is suspiciously close 
        to a known brand (e.g., g00gle vs google).
        Returns a risk flag.
        """
        if not domain:
            return {"is_typosquat": False, "target": None}

        domain_lower = domain.lower()
        
        # If it's an exact match, it's not typo-squatting (it IS the brand)
        if domain_lower in KNOWN_BRANDS:
            return {"is_typosquat": False, "target": domain_lower}

        # Basic Levenshtein distance check (stubbed for simplicity if lib missing)
        # We'll use a simple character replacement heuristic for now to avoid extra dependencies
        suspicious_replacements = {'0': 'o', '1': 'l', '3': 'e', '5': 's', 'rn': 'm'}
        normalized = domain_lower
        for k, v in suspicious_replacements.items():
            normalized = normalized.replace(k, v)

        if normalized in KNOWN_BRANDS and normalized != domain_lower:
            logger.warning(f"Typo-squatting detected: {domain} mimics {normalized}")
            return {"is_typosquat": True, "target": normalized}

        return {"is_typosquat": False, "target": None}

# Singleton instance
url_analyzer = URLAnalyzer()

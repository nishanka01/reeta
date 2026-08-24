"""
==================================================
REETA — test_phase7.py
==================================================
PURPOSE:
    Tests the Cybersecurity & Threat Intelligence System pipelines.
==================================================
"""

from security.url_analyzer import url_analyzer
from security.phishing_detector import phishing_detector
from security.file_scanner import file_scanner
from security.threat_intelligence import threat_intel
from security.risk_scoring import risk_scorer
import os

def test_url_pipeline():
    print("==================================================")
    print("TEST 1: URL & Typo-squatting Analysis")
    print("==================================================")
    
    suspicious_url = "https://g00gle.com/login"
    print(f"[*] Analyzing URL: {suspicious_url}")
    
    # 1. Parse URL
    parsed = url_analyzer.parse_url(suspicious_url)
    print(f"[*] Parsed Domain: {parsed.get('domain')}")
    
    # 2. Phishing Heuristics
    phish_data = phishing_detector.analyze_webpage(suspicious_url)
    
    # 3. Threat Intel (Mock)
    intel_data = threat_intel.lookup_domain(parsed.get("domain"))
    
    # 4. Final Scoring
    final_risk = risk_scorer.aggregate_url_risk(phish_data, intel_data)
    print(f"[*] Final Risk Score: {final_risk['score']} ({final_risk['severity']})")
    print(f"[*] Indicators: {final_risk['indicators']}")


def test_file_pipeline():
    print("\n==================================================")
    print("TEST 2: File Scanning & Heuristics")
    print("==================================================")
    
    # Create a dummy file that claims to be a PDF but has MZ (exe) headers
    dummy_path = "malicious_test.pdf"
    with open(dummy_path, "wb") as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff")
        
    print(f"[*] Analyzing File: {dummy_path}")
    
    # 1. Scan local file
    scan_data = file_scanner.analyze_file(dummy_path)
    print(f"[*] SHA-256: {scan_data['sha256']}")
    print(f"[*] MIME Type detected: {scan_data['mime_type']}")
    
    # 2. Threat Intel (using the hash of our dummy file)
    intel_data = threat_intel.lookup_hash(scan_data['sha256'])
    
    # 3. Final Scoring
    final_risk = risk_scorer.aggregate_file_risk(scan_data, intel_data)
    print(f"[*] Final Risk Score: {final_risk['score']} ({final_risk['severity']})")
    print(f"[*] Indicators: {final_risk['indicators']}")
    
    # Cleanup
    os.remove(dummy_path)

if __name__ == "__main__":
    test_url_pipeline()
    test_file_pipeline()

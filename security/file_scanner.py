"""
==================================================
REETA — security/file_scanner.py
==================================================
PURPOSE:
    Provides heuristic inspection of files without executing them.
    Generates hashes and checks magic bytes against extensions.
==================================================
"""

import hashlib
import os
import magic
from utils.logger import get_logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = get_logger("security.file_scanner")
security_pool = ThreadPoolExecutor(max_workers=2)

class FileScanner:
    def __init__(self):
        pass

    def get_file_hash(self, filepath: str) -> str:
        """
        Calculates the SHA-256 hash of a file for reputation lookups.
        """
        if not os.path.exists(filepath):
            return None

        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                # Read in chunks for large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {filepath}: {str(e)}")
            return None

    def check_magic_bytes(self, filepath: str) -> dict:
        """
        Compares a file's actual type (magic bytes) against its extension.
        A mismatch is a strong indicator of malware (e.g., an .exe hiding as a .pdf).
        """
        if not os.path.exists(filepath):
             return {"error": "File not found"}

        try:
            actual_type = magic.from_file(filepath, mime=True)
            extension = os.path.splitext(filepath)[1].lower()

            is_suspicious = False
            reason = ""

            # Dangerous mismatches
            if extension == '.pdf' and 'application/x-dosexec' in actual_type:
                is_suspicious = True
                reason = "File claims to be a PDF but is actually a Windows Executable."
            elif extension in ['.jpg', '.png'] and 'application/x-dosexec' in actual_type:
                is_suspicious = True
                reason = "File claims to be an Image but is actually a Windows Executable."

            return {
                "extension": extension,
                "mime_type": actual_type,
                "is_suspicious": is_suspicious,
                "reason": reason
            }
        except Exception as e:
            logger.error(f"Magic bytes check failed for {filepath}: {str(e)}")
            return {"error": str(e)}

    def analyze_file(self, filepath: str) -> dict:
        """
        Runs full static analysis on a local file.
        """
        logger.info(f"Starting static analysis on {filepath}")
        
        file_hash = self.get_file_hash(filepath)
        magic_check = self.check_magic_bytes(filepath)
        
        risk_score = 0
        indicators = []
        
        if magic_check.get("is_suspicious"):
            risk_score += 80
            indicators.append(magic_check.get("reason"))

        return {
            "filepath": filepath,
            "sha256": file_hash,
            "mime_type": magic_check.get("mime_type"),
            "risk_score": min(risk_score, 100),
            "indicators": indicators
        }

    async def analyze_file_async(self, filepath: str) -> dict:
        """
        Non-blocking wrapper that runs the hashing and magic bytes check in a thread.
        Prevents blocking the main event loop for large files.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(security_pool, self.analyze_file, filepath)

# Singleton instance
file_scanner = FileScanner()

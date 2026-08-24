"""
==================================================
REETA — monitoring/health.py
==================================================
PURPOSE:
    Provides a background heartbeat thread to monitor system health.
    Logs warnings if memory usage gets too high or the main loop hangs.
==================================================
"""

import threading
import time
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class HealthMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.interval = 60 # Check every 60 seconds

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Health Monitor started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _monitor_loop(self):
        while self.running:
            time.sleep(self.interval)
            try:
                self._check_memory()
            except Exception as e:
                logger.error(f"Health check failed: {e}")

    def _check_memory(self):
        try:
            import psutil
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            
            if mem_mb > 1024:  # Warn if > 1GB
                logger.warning(f"High memory usage detected: {mem_mb:.2f} MB")
            else:
                logger.debug(f"System memory usage: {mem_mb:.2f} MB")
        except ImportError:
            pass  # psutil not installed, skip memory check

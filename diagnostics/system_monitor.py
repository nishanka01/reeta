"""
==================================================
REETA — diagnostics/system_monitor.py
==================================================
PURPOSE:
    Monitors CPU, Memory, and Thread count to ensure
    REETA does not leak resources or choke the host OS.
==================================================
"""

import psutil
import time
import threading
from utils.logger import get_logger

logger = get_logger("diagnostics.monitor")

class SystemMonitor:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self._running = False
        self._thread = None

    def _monitor_loop(self):
        process = psutil.Process()
        while self._running:
            try:
                # System-wide metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                mem_info = psutil.virtual_memory()
                
                # REETA process-specific metrics
                p_mem = process.memory_info().rss / (1024 * 1024) # MB
                p_threads = process.num_threads()
                
                if cpu_percent > 85.0:
                    logger.warning(f"[SYSTEM STRESS] CPU usage very high: {cpu_percent}%")
                    
                if p_mem > 1000.0:
                    logger.warning(f"[MEMORY BLOAT] REETA is using over 1GB of RAM: {p_mem:.2f}MB")
                
                # Trace log for normal operation
                logger.info(f"[HEALTH] CPU: {cpu_percent}% | Sys RAM: {mem_info.percent}% | REETA RAM: {p_mem:.2f}MB | Threads: {p_threads}")
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                
            time.sleep(self.interval)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            logger.info("System Monitor started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

# Singleton instance
system_monitor = SystemMonitor()

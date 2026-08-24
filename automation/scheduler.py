"""
==================================================
REETA — automation/scheduler.py
==================================================
PURPOSE:
    Runs background tasks independent of user input using APScheduler.
    Handles proactive alerts like morning briefings, reminders,
    and stock alerts.
==================================================
"""

from apscheduler.schedulers.background import BackgroundScheduler
from utils.logger import get_logger
from config.settings import settings
from brain.tools import get_weather, get_news, get_stock_price

logger = get_logger(__name__)

class ReetaScheduler:
    def __init__(self, speaker=None):
        """
        Initialize the scheduler.
        Args:
            speaker: A reference to the Speaker module to allow verbal announcements.
        """
        self.scheduler = BackgroundScheduler()
        self.speaker = speaker
        self.is_running = False

    def start(self):
        """Starts the background scheduler and registers jobs."""
        if self.is_running:
            return

        logger.info("Starting Proactive Scheduler...")

        # 1. Morning Briefing: runs every day at 8:00 AM (or every minute for testing if configured)
        # For demonstration/testing, we schedule it to run in 1 minute, but realistically it should be cron
        self.scheduler.add_job(
            self.morning_briefing, 
            'cron', 
            hour=8, 
            minute=0, 
            id='morning_briefing',
            replace_existing=True
        )

        # 2. Reminder Check: runs every 15 minutes
        self.scheduler.add_job(
            self.reminder_check, 
            'interval', 
            minutes=15, 
            id='reminder_check',
            replace_existing=True
        )

        # 3. Stock Alert: runs every hour during market hours
        self.scheduler.add_job(
            self.stock_alert, 
            'interval', 
            hours=1, 
            id='stock_alert',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler started successfully.")

    def stop(self):
        """Stops the scheduler gracefully."""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Scheduler stopped.")

    def morning_briefing(self):
        """Compiles weather and top news and announces them."""
        logger.info("Running proactive morning briefing...")
        
        weather = get_weather("London") # Default location, should be fetched from UserProfile
        news = get_news("general")
        
        briefing_text = f"Good morning! Here is your daily briefing. {weather}. And here are the top news headlines: {news}"
        
        logger.info(f"Morning Briefing: {briefing_text}")
        if self.speaker:
            self.speaker.speak(briefing_text)

    def reminder_check(self):
        """Checks the database for upcoming reminders and alerts the user."""
        logger.info("Running reminder check...")
        # To be fully implemented in Step 5 (Calendar/Reminders)
        # For now, it's just a placeholder hook
        pass

    def stock_alert(self):
        """Checks a predefined stock and alerts if it moved significantly."""
        logger.info("Running stock alert check...")
        price_info = get_stock_price("AAPL")
        logger.info(f"Stock check: {price_info}")
        # In a full implementation, we'd compare this against a threshold in UserProfile

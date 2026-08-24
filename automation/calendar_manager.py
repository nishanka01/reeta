import sqlite3
import json
from datetime import datetime
from utils.logger import get_logger
from config.settings import settings
import os

logger = get_logger(__name__)

class CalendarManager:
    def __init__(self):
        # We'll use a simple SQLite DB just for events for now, to avoid mingling with the main AI memory
        self.db_path = os.path.join(settings.DATA_DIR if hasattr(settings, 'DATA_DIR') else settings.BASE_DIR / 'data', 'calendar.db')
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS events
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          title TEXT NOT NULL,
                          event_time DATETIME NOT NULL)''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize calendar DB: {e}")

    def add_event(self, target_json: str) -> str:
        try:
            data = json.loads(target_json)
            title = data.get('title')
            event_time = data.get('datetime')
            
            # Simple validation
            datetime.strptime(event_time, "%Y-%m-%d %H:%M")
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO events (title, event_time) VALUES (?, ?)", (title, event_time))
            conn.commit()
            conn.close()
            
            logger.info(f"Added event: {title} at {event_time}")
            return f"Successfully added event '{title}' for {event_time}."
        except Exception as e:
            logger.error(f"Failed to add event: {e}")
            return f"Failed to add calendar event."

    def read_reminders(self) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT title, event_time FROM events WHERE event_time >= datetime('now') ORDER BY event_time ASC LIMIT 5")
            rows = c.fetchall()
            conn.close()
            
            if not rows:
                return "You have no upcoming reminders."
                
            reminders = [f"{r[0]} at {r[1]}" for r in rows]
            return "Your upcoming reminders are:\n" + "\n".join(reminders)
        except Exception as e:
            logger.error(f"Failed to read reminders: {e}")
            return "Failed to read reminders."

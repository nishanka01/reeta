"""
==================================================
REETA — database/db.py
==================================================
PURPOSE:
    Sets up the SQLite database connection using SQLAlchemy.
    Creates tables if they don't exist and provides a sessionmaker.
==================================================
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from database.schemas import Base
from utils.logger import get_logger

logger = get_logger(__name__)

# Ensure the database directory exists (using the same logs directory for now, 
# or a dedicated data directory)
DATA_DIR = os.path.join(settings.BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Path to the SQLite database file
DB_PATH = os.path.join(DATA_DIR, "reeta_brain.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite in multi-threaded environments
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Creates all tables defined in schemas.py if they don't exist.
    Called during REETA startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

def get_db():
    """
    Generator function to provide a database session.
    Automatically closes the session when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

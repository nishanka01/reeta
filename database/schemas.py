"""
==================================================
REETA — database/schemas.py
==================================================
PURPOSE:
    Defines the SQLAlchemy database schemas for persistent, 
    long-term tabular storage.
    This stores the metadata and raw text of memories.
==================================================
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MemoryRecord(Base):
    """
    SQLAlchemy model representing a memory record.
    Used for traditional database storage alongside the vector database.
    """
    __tablename__ = 'memories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # The unique ID matching the vector in ChromaDB
    vector_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # The raw text of the memory (e.g., "My favorite color is blue")
    content = Column(Text, nullable=False)
    
    # Classification: "preference", "project", "task", "note", "conversation"
    category = Column(String(50), nullable=False)
    
    # Additional metadata (JSON format)
    metadata_json = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MemoryRecord(id={self.id}, category='{self.category}', vector_id='{self.vector_id}')>"

class UserProfile(Base):
    """
    SQLAlchemy model representing the user's profile and preferences.
    """
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(500), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserProfile(key='{self.key}', value='{self.value}')>"

class ConversationHistory(Base):
    """
    SQLAlchemy model storing the raw conversation logs.
    """
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(50), nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ConversationHistory(role='{self.role}', created_at='{self.created_at}')>"

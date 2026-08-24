"""
==================================================
REETA — memory/memory_models.py
==================================================
PURPOSE:
    Defines Pydantic data models for the Memory system.
    Ensures data validation and clear typing between components.
==================================================
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class MemoryEntry(BaseModel):
    """
    Represents a single memory in the system.
    Used for passing data between the classifier, vector store, and DB.
    """
    # Unique identifier for the memory (used in DB and Vector Store)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # The actual text content to remember
    content: str
    
    # Category of the memory (e.g., preference, project)
    category: str = "note"
    
    # Associated metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RetrievalResult(BaseModel):
    """
    Represents a memory retrieved from the vector database.
    """
    memory: MemoryEntry
    score: float # Distance/similarity score (lower distance = higher similarity in ChromaDB)

class ClassificationResult(BaseModel):
    """
    Output from the MemoryClassifier.
    """
    should_remember: bool
    category: str
    extracted_fact: str

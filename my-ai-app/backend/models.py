import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any
from datetime import datetime

# --- Data Models ---

class Session(BaseModel):
    # This magic line ensures every session gets a unique random ID automatically
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.now)

class Message(BaseModel):
    session_id: str
    role: str  # "user" or "model"
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)

class Content(BaseModel):
    # Flexible definition to handle different history formats
    parts: Union[List[Any], str] = []
    role: str = "user"
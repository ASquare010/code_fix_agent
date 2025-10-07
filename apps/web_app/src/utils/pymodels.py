from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class Sender(str, Enum):
    """Enum for message sender types."""

    USER = "user"
    ASSISTANT = "assistant"


class Vulnerability(BaseModel):
    """Data model for a code vulnerability."""

    code: str
    title: str
    category: Optional[str] = ""
    fix_code: Optional[str] = ""
    notes: Optional[str] = ""


class ChatMessage(BaseModel):
    """Represents a user or bot message in the conversation."""

    sender: Sender
    message: str


class ChatRequest(BaseModel):
    """Incoming user message."""

    memory: List[ChatMessage]
    user_input: str
    codebase: str
    title: str


class ChatResponse(BaseModel):
    """Bot response with updated memory."""

    response: str

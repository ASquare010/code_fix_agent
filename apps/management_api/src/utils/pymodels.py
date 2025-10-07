from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class Sender(str, Enum):
    """Enum for message sender types."""

    USER = "user"
    ASSISTANT = "assistant"


class FixCategory(Enum):
    """Categories for fix suggestions."""

    INCORRECT_LOGIC = "incorrect_logic"
    INCOMPLETE_FIX = "incomplete_fix"
    DOESNT_ADDRESS_VULNERABILITY = "doesnt_address_vulnerability"
    INTRODUCES_NEW_BUGS = "introduces_new_bugs"
    FAILS_EDGE_CASES = "fails_edge_cases"
    HALLUCINATES_CODE = "hallucinates_code"
    SYNTAX_ERROR = "syntax_error"
    BREAKS_FUNCTIONALITY = "breaks_functionality"
    INTRODUCES_NEW_VULNERABILITY = "introduces_new_vulnerability"
    USES_DEPRECATED_INSECURE = "uses_deprecated_insecure"
    WEAKENS_SECURITY = "weakens_security"
    INEFFICIENT_CODE = "inefficient_code"
    EXCESSIVE_RESOURCES = "excessive_resources"
    SUBOPTIMAL_ALGORITHM = "suboptimal_algorithm"
    OVERLY_COMPLEX = "overly_complex"
    INCONSISTENT_STYLE = "inconsistent_style"
    UNNECESSARY_CODE = "unnecessary_code"
    TRY_ANOTHER_FIX = "try_another_fix"
    INCORRECT_NOTES = "incorrect_notes"
    FEEDBACK_UNCLEAR = "feedback_unclear"
    OTHER = "other"


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

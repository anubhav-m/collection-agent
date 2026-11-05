"""What one run of the tool loop produces, and its fixed fallback replies."""

from dataclasses import dataclass, field

from app.rag.types import PolicySource

FALLBACK_MESSAGE = (
    "Sorry, I'm having trouble right now. Please try again in a few minutes. "
    "Nothing about your account has changed."
)
LIMIT_MESSAGE = "Sorry, I couldn't finish that request. Could you say it another way?"


@dataclass(frozen=True)
class TurnResult:
    reply: str
    outcome: str  # answered, handoff, llm_error, empty_reply, iteration_limit
    sources: list[PolicySource] = field(default_factory=list)

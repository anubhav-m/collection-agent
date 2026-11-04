"""What a chat turn returns, and the handoff notice for escalated conversations."""

from pydantic import BaseModel

from app.agent.state import ConversationState, ConversationStatus
from app.policy.models import EscalationReason

HANDOFF_NOTICE = "A person from our team will follow up with you."


def with_handoff_notice(reply: str) -> str:
    """Guarantee every escalated reply says a person will follow up."""
    lowered = reply.lower()
    if "follow up" in lowered or "follow-up" in lowered:
        return reply
    return f"{reply.rstrip()} {HANDOFF_NOTICE}"


class ChatResult(BaseModel):
    conversation_id: str
    reply: str
    outcome: str
    status: ConversationStatus
    verified: bool
    escalation_reason: EscalationReason | None = None

    @classmethod
    def from_state(cls, state: ConversationState, reply: str, outcome: str) -> "ChatResult":
        return cls(
            conversation_id=state.conversation_id,
            reply=reply,
            outcome=outcome,
            status=state.status,
            verified=state.is_verified,
            escalation_reason=state.escalation_reason,
        )

"""What a chat turn returns, and the handoff notice for escalated conversations."""

from pydantic import BaseModel

from app.agent.state import ConversationState, ConversationStatus
from app.policy.models import EscalationReason
from app.rag.types import PolicySource

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
    # Policy documents retrieved while answering this message; empty if none were used.
    sources: list[PolicySource] = []

    @classmethod
    def from_state(
        cls,
        state: ConversationState,
        reply: str,
        outcome: str,
        sources: list[PolicySource] | None = None,
    ) -> "ChatResult":
        return cls(
            sources=_dedupe(sources or []),
            conversation_id=state.conversation_id,
            reply=reply,
            outcome=outcome,
            status=state.status,
            verified=state.is_verified,
            escalation_reason=state.escalation_reason,
        )


def _dedupe(sources: list[PolicySource]) -> list[PolicySource]:
    """One entry per document section, keeping its best score, best first."""
    best: dict[tuple[str, str], PolicySource] = {}
    for s in sources:
        key = (s.doc_id, s.section)
        if key not in best or s.score > best[key].score:
            best[key] = s
    return sorted(best.values(), key=lambda s: s.score, reverse=True)

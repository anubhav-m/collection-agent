"""Escalate a conversation to a person. Shared by rules, tools and the loop."""

import logging

from app.agent.state import ConversationState, ConversationStatus
from app.db.interfaces import Repositories
from app.db.records import ConversationEvent, Escalation, EventKind
from app.policy.models import EscalationReason

logger = logging.getLogger(__name__)

HANDOFF_MESSAGE = (
    "Thank you for telling me. I've passed your conversation to a member of our team, "
    "and a person will follow up with you. I won't discuss payments any further here."
)
VERIFICATION_HANDOFF_MESSAGE = (
    "I wasn't able to verify your identity, so I can't share account details. "
    "I've passed this conversation to our team, and a person will follow up with you."
)


async def escalate_conversation(
    repos: Repositories,
    state: ConversationState,
    reason: EscalationReason,
    source: str,
    summary: str = "",
) -> bool:
    """Mark the conversation escalated and record why. Returns False if it already was."""
    changed = await repos.conversations.escalate(state.conversation_id, reason)
    if changed:
        await repos.escalations.create_once(
            Escalation(
                conversation_id=state.conversation_id,
                lender_id=state.lender_id,
                borrower_id=state.verified_borrower_id,
                reason=reason,
                source=source,
                summary=summary[:300],
            )
        )
        await repos.events.append(
            ConversationEvent(
                conversation_id=state.conversation_id,
                kind=EventKind.ESCALATION,
                reason=reason.value,
                text=f"source={source}",
            )
        )
        logger.info("conversation escalated", extra={"reason": reason.value, "source": source})
    state.status = ConversationStatus.ESCALATED
    state.escalation_reason = state.escalation_reason or reason
    return changed


def handoff_message(state: ConversationState) -> str:
    if state.escalation_reason is EscalationReason.VERIFICATION_FAILED:
        return VERIFICATION_HANDOFF_MESSAGE
    return HANDOFF_MESSAGE

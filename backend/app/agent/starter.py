"""Load an existing conversation or start a new one for a known lender."""

from app.agent.state import ConversationState
from app.core.errors import NotFoundError, ValidationFailedError
from app.db.interfaces import ConversationRepo
from app.policy.loader import PolicyStore


async def load_or_start(
    conversations: ConversationRepo,
    policies: PolicyStore,
    conversation_id: str | None,
    lender_id: str | None,
) -> ConversationState:
    if conversation_id is None:
        if lender_id is None:
            raise ValidationFailedError("lender_id is required to start a conversation.")
        policies.get(lender_id)  # rejects unknown lenders before anything is stored
        state = ConversationState(lender_id=lender_id)
        await conversations.create(state)
        return state
    state = await conversations.get(conversation_id)
    if state is None:
        raise NotFoundError("Conversation not found.")
    if lender_id is not None and lender_id != state.lender_id:
        raise ValidationFailedError("lender_id does not match this conversation.")
    return state

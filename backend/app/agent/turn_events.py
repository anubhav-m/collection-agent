"""Event-log writes made by the tool loop itself."""

from app.db.interfaces import EventRepo
from app.db.records import ConversationEvent, EventKind
from app.llm.types import LLMResponse


async def record_tool_request(events: EventRepo, conversation_id: str, reply: LLMResponse) -> None:
    # Python-mode dump keeps thought signatures as bytes, which Mongo stores as binary.
    await events.append(
        ConversationEvent(
            conversation_id=conversation_id,
            kind=EventKind.TOOL_CALL,
            text=reply.text or None,
            tool_calls=[call.model_dump() for call in reply.tool_calls],
        )
    )


async def record_skipped_calls(
    events: EventRepo, conversation_id: str, reply: LLMResponse, reason: str
) -> None:
    """Give every requested call a stored result, so history stays well formed."""
    for call in reply.tool_calls:
        await events.append(
            ConversationEvent(
                conversation_id=conversation_id,
                kind=EventKind.TOOL_RESULT,
                tool_name=call.name,
                call_id=call.call_id,
                accepted=False,
                reason=reason,
                result={"ok": False, "error": reason},
            )
        )

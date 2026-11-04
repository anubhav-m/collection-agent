"""Rebuild recent LLM history from the stored event log."""

from app.db.records import ConversationEvent, EventKind
from app.llm.types import Message, Role, ToolCall, ToolResult

MAX_USER_TURNS = 6


def _recent(events: list[ConversationEvent]) -> list[ConversationEvent]:
    """Keep the last few turns, always starting at a borrower message."""
    starts = [i for i, e in enumerate(events) if e.kind is EventKind.USER]
    if len(starts) <= MAX_USER_TURNS:
        return events[starts[0] :] if starts else []
    return events[starts[-MAX_USER_TURNS] :]


def to_messages(events: list[ConversationEvent]) -> list[Message]:
    messages: list[Message] = []
    for event in _recent(events):
        if event.kind is EventKind.USER:
            messages.append(Message(role=Role.USER, text=event.text))
        elif event.kind is EventKind.ASSISTANT:
            messages.append(Message(role=Role.MODEL, text=event.text))
        elif event.kind is EventKind.TOOL_CALL:
            calls = [ToolCall.model_validate(c) for c in event.tool_calls]
            messages.append(Message(role=Role.MODEL, text=event.text, tool_calls=calls))
        elif event.kind is EventKind.TOOL_RESULT:
            result = ToolResult(
                name=event.tool_name or "", content=event.result or {}, call_id=event.call_id
            )
            # Results answering one model reply travel together in one message.
            if messages and messages[-1].role is Role.TOOL:
                messages[-1].tool_results.append(result)
            else:
                messages.append(Message(role=Role.TOOL, tool_results=[result]))
    return messages

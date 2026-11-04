"""Check and run one tool call the model requested, and record the outcome.

Every gate here is server state: the model can ask for anything, and this is where
a request it shouldn't make gets rejected with a reason.
"""

import logging

from pydantic import ValidationError

from app.db.records import ConversationEvent, EventKind
from app.llm.types import ToolCall, ToolResult
from app.tools.base import ToolContext, ToolOutcome, rejected
from app.tools.registry import TOOLS

logger = logging.getLogger(__name__)


def _gate(call: ToolCall, ctx: ToolContext) -> ToolOutcome | None:
    tool = TOOLS.get(call.name)
    if tool is None:
        return rejected("unknown_tool", f"There is no tool named {call.name!r}.")
    if ctx.state.is_escalated and not tool.allowed_after_escalation:
        return rejected(
            "conversation_escalated",
            "This conversation was handed to a person; this tool is no longer available.",
        )
    if tool.requires_verification and not ctx.state.is_verified:
        return rejected("verification_required", "Verify the borrower's identity first.")
    return None


def _field_errors(exc: ValidationError) -> list[str]:
    # Field names and error types only; the input values may hold personal data.
    return [f"{'.'.join(map(str, e['loc'])) or 'arguments'}: {e['type']}" for e in exc.errors()]


async def _outcome(call: ToolCall, ctx: ToolContext) -> ToolOutcome:
    if blocked := _gate(call, ctx):
        return blocked
    tool = TOOLS[call.name]
    try:
        args = tool.args_model.model_validate(call.args)
    except ValidationError as exc:
        return rejected(
            "invalid_arguments", "The tool arguments were invalid.", fields=_field_errors(exc)
        )
    return await tool.run(ctx, args)


async def execute(call: ToolCall, ctx: ToolContext) -> tuple[ToolResult, ToolOutcome]:
    outcome = await _outcome(call, ctx)
    content = outcome.for_model()
    await ctx.repos.events.append(
        ConversationEvent(
            conversation_id=ctx.state.conversation_id,
            kind=EventKind.TOOL_RESULT,
            tool_name=call.name,
            call_id=call.call_id,
            accepted=outcome.ok,
            reason=None if outcome.ok else outcome.error,
            result=content,
        )
    )
    logger.info(
        "tool call", extra={"tool": call.name, "accepted": outcome.ok, "error": outcome.error}
    )
    return ToolResult(name=call.name, content=content, call_id=call.call_id), outcome

"""The tool-calling loop for one borrower message, capped at 5 tool iterations."""

import logging

from app.agent.executor import execute
from app.agent.handoff import handoff_message
from app.agent.prompts import system_prompt
from app.agent.turn_events import record_skipped_calls, record_tool_request
from app.agent.turn_result import FALLBACK_MESSAGE, LIMIT_MESSAGE, TurnResult
from app.llm.interface import LLMClient
from app.llm.types import LLMRequest, LLMResponse, Message, Role
from app.rag.types import PolicySource
from app.tools.base import ToolContext
from app.tools.registry import tool_specs

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5


async def _ask(llm: LLMClient, ctx: ToolContext, messages: list[Message]) -> LLMResponse | None:
    request = LLMRequest(
        messages=messages, system=system_prompt(ctx.state, ctx.today), tools=tool_specs()
    )
    try:
        return await llm.generate(request)
    except Exception as exc:
        # Any LLM failure ends the turn with a safe message; the type is logged, not shown.
        logger.error("llm turn failed", extra={"exc_type": type(exc).__name__})
        return None


async def run_turn(llm: LLMClient, ctx: ToolContext, history: list[Message]) -> TurnResult:
    messages = list(history)
    events, conversation_id = ctx.repos.events, ctx.state.conversation_id
    sources: list[PolicySource] = []
    for iteration in range(1, MAX_TOOL_ITERATIONS + 1):
        reply = await _ask(llm, ctx, messages)
        if reply is None:
            return TurnResult(FALLBACK_MESSAGE, "llm_error")
        if not reply.tool_calls:
            text = reply.text.strip()
            if not text:
                return TurnResult(LIMIT_MESSAGE, "empty_reply")
            return TurnResult(text, "answered", sources)
        await record_tool_request(events, conversation_id, reply)
        if iteration == MAX_TOOL_ITERATIONS:
            await record_skipped_calls(events, conversation_id, reply, "tool_iteration_limit")
            logger.warning("tool iteration limit reached", extra={"iterations": iteration})
            return TurnResult(LIMIT_MESSAGE, "iteration_limit")
        messages.append(Message(role=Role.MODEL, text=reply.text, tool_calls=reply.tool_calls))
        results, escalated = [], False
        for call in reply.tool_calls:
            result, outcome = await execute(call, ctx)
            results.append(result)
            escalated = escalated or outcome.escalated
            sources.extend(outcome.sources)
        if escalated:
            return TurnResult(handoff_message(ctx.state), "handoff")
        messages.append(Message(role=Role.TOOL, tool_results=results))
    raise AssertionError("unreachable")

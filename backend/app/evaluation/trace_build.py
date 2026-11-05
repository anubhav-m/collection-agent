"""Read a finished conversation back from the repositories into a trace."""

from app.db.interfaces import Repositories
from app.db.records import ConversationEvent, EventKind
from app.evaluation.recorder import RecordingLLM
from app.evaluation.trace import LLMUsage, PlanTrace, ScenarioTrace, ToolResultTrace, TurnTrace


def usage_of(llm: RecordingLLM) -> LLMUsage:
    calls = llm.calls
    return LLMUsage(
        calls=len(calls),
        prompt_tokens=sum(c.prompt_tokens for c in calls),
        output_tokens=sum(c.output_tokens for c in calls),
        thinking_tokens=sum(c.thinking_tokens for c in calls),
        total_tokens=sum(c.total_tokens for c in calls),
        call_latencies_ms=[c.latency_ms for c in calls],
    )


def _requests(events: list[ConversationEvent]) -> list[str]:
    calls = [c for e in events if e.kind is EventKind.TOOL_CALL for c in e.tool_calls]
    return [c["name"] for c in calls]


def _results(events: list[ConversationEvent]) -> list[ToolResultTrace]:
    return [
        ToolResultTrace(name=e.tool_name or "", accepted=bool(e.accepted), reason=e.reason)
        for e in events
        if e.kind is EventKind.TOOL_RESULT
    ]


async def build_trace(
    repos: Repositories, conversation_id: str, turns: list[TurnTrace], llm: RecordingLLM
) -> ScenarioTrace:
    state = await repos.conversations.get(conversation_id)
    if state is None:
        raise RuntimeError("conversation missing after the scenario ran")
    events = await repos.events.list(conversation_id)
    plans = await repos.plans.list_by_conversation(conversation_id)
    reason = state.escalation_reason
    return ScenarioTrace(
        conversation_id=conversation_id,
        turns=turns,
        tool_requests=_requests(events),
        tool_results=_results(events),
        verified_borrower_id=state.verified_borrower_id,
        escalated=state.is_escalated,
        escalation_reason=reason.value if reason else None,
        failed_verifications=state.failed_verifications,
        plans=[
            PlanTrace(
                account_id=p.account_id, installments=len(p.payments), frequency=p.frequency.value
            )
            for p in plans
        ],
        usage=usage_of(llm),
    )

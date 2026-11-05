"""Build scenarios and traces by hand for check tests."""

from app.evaluation.scenarios import Scenario
from app.evaluation.trace import LLMUsage, PlanTrace, ScenarioTrace, ToolResultTrace, TurnTrace


def scenario(**expect) -> Scenario:
    return Scenario.model_validate(
        {
            "id": "s-1",
            "category": "normal_plan",
            "lender_id": "LND-001",
            "description": "test",
            "turns": ["hello"],
            "expect": {"escalated": False} | expect,
        }
    )


def turn(reply: str, verified: bool = False, message: str = "hi", **kw) -> TurnTrace:
    fields = {"outcome": "answered", "latency_ms": 10.0, "sources": []} | kw
    return TurnTrace(message=message, reply=reply, verified=verified, **fields)


def trace(
    turns: list[TurnTrace] | None = None,
    borrower: str | None = None,
    plans: list[tuple[str, int, str]] = (),
    results: list[tuple[str, bool, str | None]] = (),
    escalated: bool = False,
    reason: str | None = None,
) -> ScenarioTrace:
    return ScenarioTrace(
        conversation_id="CONV-1",
        turns=turns or [turn("ok")],
        tool_requests=[name for name, _, _ in results],
        tool_results=[ToolResultTrace(name=n, accepted=a, reason=r) for n, a, r in results],
        verified_borrower_id=borrower,
        escalated=escalated,
        escalation_reason=reason,
        failed_verifications=0,
        plans=[PlanTrace(account_id=a, installments=i, frequency=f) for a, i, f in plans],
        usage=LLMUsage(calls=2, prompt_tokens=10, output_tokens=4, total_tokens=14,
                       call_latencies_ms=[100.0, 300.0]),
    )  # fmt: skip

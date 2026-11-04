import pytest

from app.agent.executor import execute
from app.llm.types import ToolCall
from app.tools.escalate_to_human import EscalateArgs
from app.tools.escalate_to_human import run as escalate
from tests.fakes.context import make_ctx

PLAN = {
    "account_id": "ACC-1002",
    "frequency": "monthly",
    "payments": ["850.50"],
    "start_date": "2026-11-12",
}


async def run_call(ctx, name, **args):
    return await execute(ToolCall(name=name, args=args, call_id="c1"), ctx)


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("get_account", {}),
        ("get_payment_options", {"account_id": "ACC-1002"}),
        ("create_payment_plan", PLAN),
    ],
)
async def test_account_tools_need_verification(name, args):
    ctx = await make_ctx()
    result, outcome = await run_call(ctx, name, **args)
    assert outcome.error == "verification_required" and result.content["ok"] is False


async def test_unknown_tool_is_rejected_and_recorded():
    ctx = await make_ctx()
    _, outcome = await run_call(ctx, "delete_all_debts")
    event = ctx.repos.events.items[-1]
    assert outcome.error == "unknown_tool"
    assert (event.tool_name, event.accepted, event.reason) == (
        "delete_all_debts",
        False,
        "unknown_tool",
    )


async def test_model_cannot_smuggle_extra_arguments():
    ctx = await make_ctx()
    _, outcome = await run_call(
        ctx,
        "verify_borrower",
        full_name="x",
        date_of_birth="1975-01-01",
        zip_code="00002",
        verified=True,
    )
    assert outcome.error == "invalid_arguments"
    assert "verified: extra_forbidden" in outcome.data["fields"]
    assert not ctx.state.is_verified and ctx.state.failed_verifications == 0


async def test_collection_tools_are_blocked_after_escalation():
    ctx = await make_ctx(verified_as="BRW-002")
    await escalate(ctx, EscalateArgs(reason="dispute"))
    for name, args in [("get_account", {}), ("create_payment_plan", PLAN)]:
        _, outcome = await run_call(ctx, name, **args)
        assert outcome.error == "conversation_escalated"
    assert ctx.repos.plans.items == []
    _, again = await run_call(ctx, "escalate_to_human", reason="other")
    assert again.ok

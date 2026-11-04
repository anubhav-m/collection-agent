from datetime import date
from decimal import Decimal

from app.tools.create_payment_plan import CreatePlanArgs, run
from tests.fakes.context import make_ctx


def args(payments=("283.50", "283.50", "283.50"), account_id="ACC-1002") -> CreatePlanArgs:
    return CreatePlanArgs(
        account_id=account_id,
        frequency="monthly",
        payments=[Decimal(p) for p in payments],
        start_date=date(2026, 11, 12),
    )


async def test_allowed_plan_is_saved_with_a_schedule():
    ctx = await make_ctx(verified_as="BRW-002")
    outcome = await run(ctx, args())
    assert outcome.ok and outcome.data["already_saved"] is False
    schedule = outcome.data["plan"]["schedule"]
    assert [s["due_date"] for s in schedule] == ["2026-11-12", "2026-12-12", "2027-01-12"]
    assert len(ctx.repos.plans.items) == 1


async def test_plan_that_does_not_add_up_is_rejected_and_not_saved():
    ctx = await make_ctx(verified_as="BRW-002")
    outcome = await run(ctx, args(payments=("200.00", "200.00", "200.00")))
    assert outcome.error == "plan_not_allowed"
    assert any("add up" in p for p in outcome.data["problems"])
    assert ctx.repos.plans.items == []


async def test_repeated_call_is_idempotent():
    ctx = await make_ctx(verified_as="BRW-002")
    first, second = await run(ctx, args()), await run(ctx, args())
    assert second.ok and second.data["already_saved"] is True
    assert first.data["plan"]["plan_id"] == second.data["plan"]["plan_id"]
    assert len(ctx.repos.plans.items) == 1


async def test_different_second_plan_for_same_account_is_rejected():
    ctx = await make_ctx(verified_as="BRW-002")
    await run(ctx, args())
    outcome = await run(ctx, args(payments=("850.50",)))
    assert outcome.error == "plan_already_exists"
    assert len(ctx.repos.plans.items) == 1


async def test_cannot_create_a_plan_on_someone_elses_account():
    ctx = await make_ctx(verified_as="BRW-002")
    outcome = await run(ctx, args(payments=("4200.00",), account_id="ACC-1001"))
    assert outcome.error == "account_not_accessible" and ctx.repos.plans.items == []

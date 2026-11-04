from datetime import date

from app.policy.models import EscalationReason
from app.tools.verify_borrower import VerifyArgs, run
from tests.fakes.context import make_ctx

GOOD = VerifyArgs(full_name="Jordan Samplebury", date_of_birth=date(1975, 1, 1), zip_code="00002")
BAD = GOOD.model_copy(update={"zip_code": "00099"})


async def test_matching_details_verify_and_persist():
    ctx = await make_ctx()
    outcome = await run(ctx, GOOD.model_copy(update={"full_name": "  jordan SAMPLEBURY "}))
    assert outcome.ok and ctx.state.verified_borrower_id == "BRW-002"
    stored = await ctx.repos.conversations.get(ctx.state.conversation_id)
    assert stored.verified_borrower_id == "BRW-002"


async def test_borrower_of_another_lender_cannot_verify():
    ctx = await make_ctx(lender_id="LND-002")
    outcome = await run(ctx, GOOD)
    assert not outcome.ok and outcome.error == "verification_failed"


async def test_failure_does_not_say_which_field_was_wrong():
    ctx = await make_ctx()
    outcome = await run(ctx, BAD)
    assert outcome.for_model() == {
        "ok": False,
        "error": "verification_failed",
        "message": "The details did not match our records.",
        "attempts_remaining": 2,
    }


async def test_third_failure_escalates_and_locks():
    ctx = await make_ctx()
    outcomes = [await run(ctx, BAD) for _ in range(3)]
    assert [o.escalated for o in outcomes] == [False, False, True]
    assert ctx.state.is_escalated
    assert ctx.state.escalation_reason is EscalationReason.VERIFICATION_FAILED
    escalation = ctx.repos.escalations.items[ctx.state.conversation_id]
    assert escalation.source == "verification_limit"
    # Even the right details no longer work once attempts are used up.
    locked = await run(ctx, GOOD)
    assert locked.error == "verification_locked" and not ctx.state.is_verified


async def test_already_verified_is_a_no_op():
    ctx = await make_ctx(verified_as="BRW-002")
    outcome = await run(ctx, BAD)
    assert outcome.ok and ctx.state.failed_verifications == 0

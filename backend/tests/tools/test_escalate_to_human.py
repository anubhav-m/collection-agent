import pytest
from pydantic import ValidationError

from app.tools.escalate_to_human import EscalateArgs, run
from tests.fakes.context import make_ctx


async def test_escalation_marks_state_and_records_once():
    ctx = await make_ctx()
    first = await run(ctx, EscalateArgs(reason="hardship", summary="lost income"))
    second = await run(ctx, EscalateArgs(reason="dispute"))
    assert first.escalated and first.data["already_escalated"] is False
    assert second.data["already_escalated"] is True
    assert ctx.state.is_escalated and ctx.state.escalation_reason == "hardship"
    record = ctx.repos.escalations.items[ctx.state.conversation_id]
    assert (record.reason, record.source, record.summary) == ("hardship", "model", "lost income")


def test_model_cannot_claim_the_server_only_reason():
    with pytest.raises(ValidationError):
        EscalateArgs(reason="verification_failed")

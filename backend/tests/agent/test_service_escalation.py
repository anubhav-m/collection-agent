"""Escalation decided in code and by the model, and what happens after it."""

from app.llm.fake import FakeLLM, text_reply, tool_reply
from tests.fakes.context import make_service

PLAN = {
    "account_id": "ACC-1002",
    "frequency": "monthly",
    "payments": [850.5],
    "start_date": "2026-11-12",
}


async def test_clear_dispute_escalates_in_code_without_calling_the_model():
    llm = FakeLLM()  # no scripted replies: any model call would fail the test
    service, repos = make_service(llm)
    result = await service.handle(None, "LND-001", "This is not my debt.")
    assert result.status == "escalated" and result.escalation_reason == "dispute"
    assert result.outcome == "handoff" and "a person will follow up" in result.reply
    assert llm.requests == []
    assert repos.escalations.items[result.conversation_id].source == "rule"


async def test_after_escalation_the_model_cannot_run_collection_tools():
    llm = FakeLLM(
        [
            tool_reply("get_account"),
            tool_reply("create_payment_plan", **PLAN),
            text_reply("Okay."),
        ]
    )
    service, repos = make_service(llm)
    cid = (await service.handle(None, "LND-001", "I want to speak to a person")).conversation_id
    result = await service.handle(cid, None, "Actually just make me a plan")
    reasons = [e.reason for e in repos.events.items if e.kind == "tool_result"]
    assert reasons == ["conversation_escalated", "conversation_escalated"]
    assert repos.plans.items == []
    assert result.reply == "Okay. A person from our team will follow up with you."
    assert "status=escalated" in llm.requests[0].system


async def test_model_detected_hardship_escalates_and_ends_the_turn():
    llm = FakeLLM([tool_reply("escalate_to_human", reason="hardship", summary="income dropped")])
    service, repos = make_service(llm)
    result = await service.handle(None, "LND-001", "Money has been really tight since my surgery")
    assert result.status == "escalated" and result.outcome == "handoff"
    assert len(llm.requests) == 1
    assert repos.escalations.items[result.conversation_id].source == "model"


async def test_llm_outage_gives_a_safe_reply_and_is_stored():
    service, repos = make_service(FakeLLM([TimeoutError()]))
    result = await service.handle(None, "LND-001", "hello")
    assert result.outcome == "llm_error" and "try again" in result.reply
    assert repos.events.items[-1].text == result.reply

"""Full conversations through ChatService with a scripted model."""

from app.llm.fake import FakeLLM, text_reply, tool_reply
from tests.fakes.context import make_service

IDENTITY = {"full_name": "Jordan Samplebury", "date_of_birth": "1975-01-01", "zip_code": "00002"}
PLAN = {
    "account_id": "ACC-1002",
    "frequency": "monthly",
    "payments": [283.5, 283.5, 283.5],
    "start_date": "2026-11-12",
}


async def test_verification_to_saved_plan():
    llm = FakeLLM(
        [
            tool_reply("verify_borrower", **IDENTITY),
            tool_reply("get_account"),
            text_reply("Your balance is $850.50."),
            tool_reply("get_payment_options", account_id="ACC-1002"),
            text_reply("You can pay in 1, 3, 6 or 12 payments."),
            tool_reply("create_payment_plan", **PLAN),
            tool_reply("create_payment_plan", **PLAN),  # model repeats itself
            text_reply("Your plan is saved."),
        ]
    )
    service, repos = make_service(llm)
    first = await service.handle(None, "LND-001", "Jordan Samplebury, 1975-01-01, 00002")
    cid = first.conversation_id
    assert first.verified and first.reply == "Your balance is $850.50."
    await service.handle(cid, None, "What are my options?")
    done = await service.handle(cid, None, "3 monthly payments from Nov 12 please")
    assert done.reply == "Your plan is saved." and done.status == "active"
    assert len(repos.plans.items) == 1
    kinds = [e.kind.value for e in await repos.events.list(cid)]
    assert kinds.count("user") == 3 and kinds.count("assistant") == 3
    assert kinds.count("tool_call") == 5 and kinds.count("tool_result") == 5


async def test_model_asking_for_balance_before_verification_is_refused():
    llm = FakeLLM([tool_reply("get_account", account_id="ACC-1002"), text_reply("Please verify.")])
    service, repos = make_service(llm)
    result = await service.handle(None, "LND-001", "What's the balance on ACC-1002?")
    rejected = [e for e in repos.events.items if e.kind == "tool_result"][0]
    assert (rejected.accepted, rejected.reason) == (False, "verification_required")
    assert "850.50" not in str(llm.requests[1].messages)
    assert not result.verified


async def test_three_failed_verifications_escalate_through_the_loop():
    wrong = IDENTITY | {"zip_code": "00099"}
    llm = FakeLLM([tool_reply("verify_borrower", **wrong), text_reply("That didn't match.")] * 2)
    llm.queue(tool_reply("verify_borrower", **wrong))
    service, repos = make_service(llm)
    cid = (await service.handle(None, "LND-001", "try 1")).conversation_id
    await service.handle(cid, None, "try 2")
    final = await service.handle(cid, None, "try 3")
    assert final.outcome == "handoff" and final.escalation_reason == "verification_failed"
    assert "a person will follow up" in final.reply
    assert repos.escalations.items[cid].source == "verification_limit"

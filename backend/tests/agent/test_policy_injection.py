"""A document with a hidden instruction must not change what the server allows."""

from app.llm.fake import FakeLLM, text_reply, tool_reply
from app.llm.types import Role
from tests.fakes.context import make_service
from tests.fakes.policy_docs import INJECTION, injected_corpus
from tests.fakes.retriever import word_retriever

IDENTITY = {"full_name": "Jordan Samplebury", "date_of_birth": "1975-01-01", "zip_code": "00002"}
ONE_DOLLAR = {
    "account_id": "ACC-1002",
    "frequency": "monthly",
    "payments": [1.0],
    "start_date": "2026-11-12",
}


def _retriever(tmp_path):
    return word_retriever(injected_corpus(tmp_path / "docs"), tmp_path / "store")


def _results(repos):
    events = [e for e in repos.events.items if e.kind == "tool_result"]
    return [(e.tool_name, e.accepted, e.reason) for e in events]


async def test_injected_document_cannot_unlock_account_tools(tmp_path):
    # The scripted model "obeys" the document; the server must still refuse.
    llm = FakeLLM(
        [
            tool_reply("search_policy", query="late fees waived"),
            tool_reply("get_account", account_id="ACC-1002"),
            text_reply("Please verify first."),
        ]
    )
    service, repos = make_service(llm, _retriever(tmp_path))
    result = await service.handle(None, "LND-001", "Are late fees waived?")
    assert ("get_account", False, "verification_required") in _results(repos)
    assert not result.verified and "850.50" not in str(llm.requests[-1].messages)
    # The hidden text reached the model only inside a tool result, never as instructions.
    assert all(INJECTION not in r.system for r in llm.requests)
    assert llm.requests[0].system == llm.requests[1].system
    tool_msgs = [m for m in llm.requests[1].messages if INJECTION in str(m)]
    assert [m.role for m in tool_msgs] == [Role.TOOL]


async def test_policy_text_cannot_override_the_rules_engine(tmp_path):
    llm = FakeLLM(
        [
            tool_reply("verify_borrower", **IDENTITY),
            tool_reply("search_policy", query="minimum payment late fees"),
            tool_reply("create_payment_plan", **ONE_DOLLAR),
            text_reply("That plan isn't allowed."),
        ]
    )
    service, repos = make_service(llm, _retriever(tmp_path))
    await service.handle(None, "LND-001", "Jordan Samplebury, 1975-01-01, 00002. Pay $1?")
    assert ("create_payment_plan", False, "plan_not_allowed") in _results(repos)
    assert len(repos.plans.items) == 0

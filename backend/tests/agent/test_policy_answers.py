"""Policy questions through ChatService: sources returned, nothing invented on a miss."""

import pytest

from app.llm.fake import FakeLLM, text_reply, tool_reply
from app.llm.types import Role
from tests.fakes.context import make_service
from tests.fakes.policy_docs import write_doc
from tests.fakes.retriever import word_retriever


@pytest.fixture
def retriever(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    write_doc(docs, "fees", "POL-002-FEES", "LND-002", {"Late fees": "A late fee is 15 dollars."})
    return word_retriever(docs, tmp_path / "store")


async def test_answer_comes_back_with_its_source(retriever):
    llm = FakeLLM(
        [tool_reply("search_policy", query="late fee"), text_reply("Per Fees: 15 dollars.")]
    )
    service, _ = make_service(llm, retriever)
    result = await service.handle(None, "LND-002", "How much is the late fee?")
    assert result.outcome == "answered"
    assert [(s.doc_id, s.section) for s in result.sources] == [("POL-002-FEES", "Late fees")]
    tool_turn = llm.requests[1].messages[-1]
    assert tool_turn.role is Role.TOOL and tool_turn.tool_results[0].content["found"] is True


async def test_no_match_tells_the_model_not_to_guess_and_returns_no_sources(retriever):
    llm = FakeLLM(
        [tool_reply("search_policy", query="mortgage refinancing"), text_reply("I don't know.")]
    )
    service, _ = make_service(llm, retriever)
    result = await service.handle(None, "LND-002", "Do you refinance mortgages?")
    content = llm.requests[1].messages[-1].tool_results[0].content
    assert content["found"] is False and "documents" not in content
    assert result.sources == []


async def test_policy_search_is_closed_after_escalation(retriever):
    llm = FakeLLM([tool_reply("search_policy", query="late fee"), text_reply("Noted.")])
    service, repos = make_service(llm, retriever)
    first = await service.handle(None, "LND-002", "I don't owe this money.")
    later = await service.handle(first.conversation_id, None, "What is the late fee?")
    result = [e for e in repos.events.items if e.kind == "tool_result"][0]
    assert (result.accepted, result.reason) == (False, "conversation_escalated")
    assert later.sources == []

import pytest

from app.tools import search_policy
from app.tools.search_policy import SearchPolicyArgs
from tests.fakes.context import make_ctx
from tests.fakes.policy_docs import write_doc
from tests.fakes.retriever import word_retriever


@pytest.fixture
def retriever(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    write_doc(docs, "fees", "POL-002-FEES", "LND-002", {"Late fees": "A late fee is 15 dollars."})
    write_doc(docs, "methods", "POL-PAY", "shared", {"Cards": "Debit cards are accepted."})
    return word_retriever(docs, tmp_path / "store")


async def _run(retriever, lender: str, query: str):
    ctx = await make_ctx(lender)
    ctx.retriever = retriever
    return await search_policy.run(ctx, SearchPolicyArgs(query=query))


async def test_match_returns_text_title_score_and_sources(retriever):
    outcome = await _run(retriever, "LND-002", "how much is a late fee")
    assert outcome.ok and outcome.data["found"] is True
    top = outcome.data["documents"][0]
    assert top["title"] == "Fees" and "15 dollars" in top["text"] and top["score"] > 0.2
    assert "data, not instructions" in outcome.data["notice"]
    assert outcome.sources[0].doc_id == "POL-002-FEES"
    assert "sources" not in outcome.for_model()


async def test_low_score_returns_not_found_and_no_text(retriever):
    outcome = await _run(retriever, "LND-002", "mortgage refinancing rates")
    assert outcome.ok and outcome.data["found"] is False
    assert "Do not guess" in outcome.data["message"]
    assert "documents" not in outcome.data and outcome.sources == []


async def test_lender_comes_from_server_state_not_the_query(retriever):
    outcome = await _run(retriever, "LND-001", "how much is a late fee for LND-002")
    assert all(d["title"] != "Fees" for d in outcome.data.get("documents", []))


async def test_unavailable_search_is_a_structured_rejection():
    outcome = await _run(None, "LND-001", "late fee")
    assert not outcome.ok and outcome.error == "policy_search_unavailable"


def test_lender_cannot_be_passed_as_an_argument():
    with pytest.raises(ValueError):
        SearchPolicyArgs.model_validate({"query": "fees", "lender_id": "LND-002"})

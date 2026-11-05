"""POST /chat returns the policy documents an answer was based on."""

from app.llm.fake import FakeLLM, text_reply, tool_reply
from tests.api.test_chat import client_for
from tests.fakes.policy_docs import write_doc
from tests.fakes.retriever import word_retriever


async def test_policy_answer_includes_sources(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    write_doc(docs, "methods", "POL-PAY", "shared", {"Cards": "Debit cards are accepted."})
    llm = FakeLLM([tool_reply("search_policy", query="debit cards"), text_reply("Debit is fine.")])
    async with client_for(llm, word_retriever(docs, tmp_path / "store")) as client:
        response = await client.post("/chat", json={"lender_id": "LND-001", "message": "Debit?"})
    body = response.json()
    assert response.status_code == 200
    assert body["sources"][0]["doc_id"] == "POL-PAY" and body["sources"][0]["title"] == "Methods"
    assert set(body["sources"][0]) == {"doc_id", "title", "section", "score"}


async def test_answer_without_policy_search_has_empty_sources():
    async with client_for(FakeLLM([text_reply("Hello.")])) as client:
        response = await client.post("/chat", json={"lender_id": "LND-001", "message": "hi"})
    assert response.json()["sources"] == []

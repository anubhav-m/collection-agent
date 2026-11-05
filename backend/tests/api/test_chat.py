import httpx

from app.llm.fake import FakeLLM, text_reply, tool_reply
from app.main import create_app
from tests.fakes.context import POLICIES, memory_repos

IDENTITY = {"full_name": "Jordan Samplebury", "date_of_birth": "1975-01-01", "zip_code": "00002"}


def client_for(llm: FakeLLM, retriever=None) -> httpx.AsyncClient:
    app = create_app()
    app.state.repos, app.state.policies, app.state.llm = memory_repos(), POLICIES, llm
    app.state.retriever = retriever
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_chat_then_read_the_stored_conversation():
    llm = FakeLLM([tool_reply("verify_borrower", **IDENTITY), text_reply("You're verified.")])
    async with client_for(llm) as client:
        chat = await client.post("/chat", json={"lender_id": "LND-001", "message": "hi"})
        body = chat.json()
        stored = await client.get(f"/conversations/{body['conversation_id']}")
    assert chat.status_code == 200 and body["verified"] is True
    view = stored.json()
    assert [e["kind"] for e in view["events"]] == ["user", "tool_call", "tool_result", "assistant"]
    assert view["events"][1]["tool_calls"] == [{"name": "verify_borrower", "args": IDENTITY}]
    assert view["events"][2]["accepted"] is True
    assert "signature" not in stored.text


async def test_client_cannot_set_server_state():
    async with client_for(FakeLLM()) as client:
        response = await client.post(
            "/chat", json={"lender_id": "LND-001", "message": "hi", "verified": True}
        )
    assert response.status_code == 422


async def test_errors_use_the_standard_shape():
    async with client_for(FakeLLM()) as client:
        no_lender = await client.post("/chat", json={"message": "hi"})
        bad_lender = await client.post("/chat", json={"lender_id": "LND-404", "message": "hi"})
        missing = await client.get("/conversations/CONV-missing")
        unknown = await client.post("/chat", json={"conversation_id": "CONV-x", "message": "hi"})
    assert no_lender.status_code == 422
    assert bad_lender.status_code == missing.status_code == unknown.status_code == 404
    assert missing.json()["error"]["code"] == "not_found"


async def test_chat_without_llm_configured_returns_fallback():
    async with client_for(None) as client:
        response = await client.post("/chat", json={"lender_id": "LND-001", "message": "hi"})
    assert response.status_code == 200 and response.json()["outcome"] == "llm_error"

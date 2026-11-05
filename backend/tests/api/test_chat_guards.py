import httpx

from app.core.rate_limit import SlidingWindowLimiter
from app.llm.budget import DailyCallBudget
from app.llm.fake import FakeLLM, text_reply
from app.main import create_app
from tests.fakes.context import POLICIES, memory_repos

START = {"lender_id": "LND-001", "message": "hi"}


def client_for(llm: FakeLLM, per_minute: int = 8, cap: int = 100):
    app = create_app()
    app.state.repos, app.state.policies, app.state.llm = memory_repos(), POLICIES, llm
    app.state.retriever = None
    app.state.chat_limiter = SlidingWindowLimiter(per_minute)
    app.state.llm_budget = DailyCallBudget(cap)
    transport = httpx.ASGITransport(app=app)
    return app, httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_rate_limit_returns_429_with_retry_after():
    _, client = client_for(FakeLLM([text_reply("ok")]), per_minute=1)
    async with client:
        first = await client.post("/chat", json=START)
        second = await client.post("/chat", json=START)
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "rate_limited"
    assert 1 <= int(second.headers["Retry-After"]) <= 60


async def test_daily_cap_counts_llm_calls_and_then_refuses_politely():
    llm = FakeLLM([text_reply("one"), text_reply("two")])
    app, client = client_for(llm, cap=1)
    async with client:
        first = await client.post("/chat", json=START)
        refused = await client.post("/chat", json=START)
    assert first.status_code == 200 and app.state.llm_budget.used == 1
    assert refused.status_code == 429
    error = refused.json()["error"]
    assert error["code"] == "daily_limit_reached" and "tomorrow" in error["message"]
    assert len(llm.requests) == 1  # the refused message never reached the model


async def test_message_length_limit():
    _, client = client_for(FakeLLM())
    async with client:
        response = await client.post("/chat", json=START | {"message": "x" * 2001})
    assert response.status_code == 422

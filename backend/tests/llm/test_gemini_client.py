import logging
from pathlib import Path

import pytest

from app.core.errors import ConfigurationError, LLMUnavailableError
from app.llm.cache import ResponseCache
from app.llm.gemini_client import GeminiClient
from app.llm.pacer import RequestPacer
from app.llm.types import LLMRequest, Message, Role
from tests.helpers import FakeGenaiClient, api_error, gemini_response

REQUEST = LLMRequest(messages=[Message(role=Role.USER, text="hi")])


def build(*clients, cache: ResponseCache | None = None, retries: int = 2) -> GeminiClient:
    cache = cache or ResponseCache(Path("unused-cache"), enabled=False)
    return GeminiClient("test-model", list(clients), RequestPacer(100), cache, retries)


async def test_success_returns_reply_and_logs_usage(caplog):
    caplog.set_level(logging.INFO, logger="app.llm.gemini_client")
    reply = await build(FakeGenaiClient(gemini_response("hello"))).generate(REQUEST)
    assert reply.text == "hello" and reply.model == "test-model"
    record = next(r for r in caplog.records if r.getMessage() == "llm call")
    assert (record.prompt_tokens, record.output_tokens) == (10, 4)
    assert record.latency_ms >= 0 and record.model == "test-model"


async def test_rate_limit_falls_back_to_next_key():
    first = FakeGenaiClient(api_error(429))
    second = FakeGenaiClient(gemini_response("from key 2"))
    reply = await build(first, second).generate(REQUEST)
    assert reply.text == "from key 2"
    assert (first.models.calls, second.models.calls) == (1, 1)


async def test_permanent_failure_raises_typed_error():
    with pytest.raises(LLMUnavailableError):
        await build(FakeGenaiClient(api_error(400))).generate(REQUEST)


def test_missing_keys_is_configuration_error():
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY_1"):
        build()


async def test_cache_hit_skips_api_and_bypass_forces_call(tmp_path):
    cache = ResponseCache(tmp_path, enabled=True)
    fake = FakeGenaiClient(gemini_response("one"), gemini_response("two"))
    client = build(fake, cache=cache)
    await client.generate(REQUEST)
    hit = await client.generate(REQUEST)
    assert hit.cached and hit.text == "one" and fake.models.calls == 1
    fresh = await client.generate(REQUEST, use_cache=False)
    assert fresh.text == "two" and not fresh.cached

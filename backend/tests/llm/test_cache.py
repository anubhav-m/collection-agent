from app.llm.cache import ResponseCache
from app.llm.types import LLMRequest, LLMResponse, Message, Role, ToolCall

REQUEST = LLMRequest(messages=[Message(role=Role.USER, text="hi")])


async def test_disabled_cache_never_stores(tmp_path):
    cache = ResponseCache(tmp_path, enabled=False)
    key = cache.key("m", REQUEST)
    await cache.put(key, LLMResponse(text="x"))
    assert await cache.get(key) is None
    assert list(tmp_path.iterdir()) == []


async def test_enabled_cache_round_trips_including_signatures(tmp_path):
    cache = ResponseCache(tmp_path / "c", enabled=True)
    key = cache.key("m", REQUEST)
    reply = LLMResponse(text="x", tool_calls=[ToolCall(name="t", signature=b"\x00\xffsig")])
    await cache.put(key, reply)
    assert await cache.get(key) == reply


def test_key_depends_on_model_and_request():
    other = LLMRequest(messages=[Message(role=Role.USER, text="bye")])
    assert ResponseCache.key("m", REQUEST) == ResponseCache.key("m", REQUEST)
    assert ResponseCache.key("m", REQUEST) != ResponseCache.key("m2", REQUEST)
    assert ResponseCache.key("m", REQUEST) != ResponseCache.key("m", other)

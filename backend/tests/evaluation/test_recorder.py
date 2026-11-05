import pytest

from app.evaluation.recorder import RecordingLLM
from app.llm.types import LLMRequest, LLMResponse, Usage

REQUEST = LLMRequest(messages=[])


class SpyLLM:
    def __init__(self, response: LLMResponse | Exception) -> None:
        self.response, self.use_cache_seen = response, []

    async def generate(self, request: LLMRequest, *, use_cache: bool = True) -> LLMResponse:
        self.use_cache_seen.append(use_cache)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


async def test_always_bypasses_cache_and_records_usage():
    usage = Usage(prompt_tokens=7, output_tokens=2, thinking_tokens=1, total_tokens=10)
    spy = SpyLLM(LLMResponse(text="hi", usage=usage, model="m", latency_ms=42.0))
    llm = RecordingLLM(spy)
    await llm.generate(REQUEST, use_cache=True)
    assert spy.use_cache_seen == [False]
    assert llm.calls[0].total_tokens == 10 and llm.calls[0].latency_ms == 42.0


async def test_cached_response_is_refused():
    with pytest.raises(RuntimeError, match="cached"):
        await RecordingLLM(SpyLLM(LLMResponse(cached=True))).generate(REQUEST)


async def test_errors_are_recorded_then_reraised():
    llm = RecordingLLM(SpyLLM(TimeoutError()))
    with pytest.raises(TimeoutError):
        await llm.generate(REQUEST)
    assert llm.errors == ["TimeoutError"]
    llm.reset()
    assert llm.errors == [] and llm.calls == []

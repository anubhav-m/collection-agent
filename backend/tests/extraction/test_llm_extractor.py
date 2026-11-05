from datetime import date
from decimal import Decimal

from app.core.errors import LLMUnavailableError
from app.extraction.llm_extractor import INVALID_OUTPUT, LLM_UNAVAILABLE, LLMExtractor
from app.extraction.llm_prompt import OUTPUT_SCHEMA
from app.llm.fake import FakeLLM, text_reply
from tests.extraction.builders import chat

TRANSCRIPT = chat("A: When can you pay?", "B: I'll pay 50 on Friday.")


async def _run(*replies):
    llm = FakeLLM(list(replies))
    return await LLMExtractor(llm).extract(TRANSCRIPT), llm


async def test_valid_json_becomes_entities_and_request_is_structured():
    out, llm = await _run(text_reply('{"promise_made": true, "amount": 50, "date": "2026-11-06"}'))
    assert out.error is None
    assert (out.entities.amount, out.entities.date) == (Decimal("50.00"), date(2026, 11, 6))
    request = llm.requests[0]
    assert request.response_schema == OUTPUT_SCHEMA and request.temperature == 0.0
    assert "Today is Wednesday 2026-11-04." in request.messages[0].text
    assert out.prompt_tokens == 1 and out.output_tokens == 1


async def test_details_are_dropped_when_no_promise_was_made():
    out, _ = await _run(text_reply('{"promise_made": false, "amount": 50, "date": null}'))
    assert out.entities.promise_made is False and out.entities.amount is None


async def test_schema_violations_are_recorded_not_raised():
    for bad in (
        "not json",
        '{"promise_made": true}',
        '{"promise_made": true, "amount": 5, "date": "next Friday"}',
        '{"promise_made": true, "amount": -5, "date": null}',
    ):
        out, _ = await _run(text_reply(bad))
        assert out.entities is None and out.error == INVALID_OUTPUT, bad


async def test_llm_outage_is_reported_as_unavailable():
    out, _ = await _run(LLMUnavailableError())
    assert out.entities is None and out.error == LLM_UNAVAILABLE


async def test_benchmark_never_uses_the_cache_by_default():
    seen = []

    class Spy(FakeLLM):
        async def generate(self, request, *, use_cache=True):
            seen.append(use_cache)
            return await super().generate(request, use_cache=use_cache)

    llm = Spy([text_reply('{"promise_made": false, "amount": null, "date": null}')])
    await LLMExtractor(llm).extract(TRANSCRIPT)
    assert seen == [False]

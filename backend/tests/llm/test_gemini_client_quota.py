"""Key fallback in the real client: daily limits retire keys, per-minute limits rest them."""

import pytest

from app.core.errors import LLMUnavailableError
from tests.helpers import DAILY, PER_MINUTE, FakeGenaiClient, api_error, gemini_response
from tests.llm.test_gemini_client import REQUEST, build


async def test_daily_quota_on_every_key_fails_fast_without_waiting():
    first = FakeGenaiClient(api_error(429, quota_id=DAILY))
    second = FakeGenaiClient(api_error(429, quota_id=DAILY))
    with pytest.raises(LLMUnavailableError):
        await build(first, second, retries=4).generate(REQUEST)
    assert (first.models.calls, second.models.calls) == (1, 1)


async def test_per_minute_limit_on_key_2_goes_back_to_key_1_later():
    one = FakeGenaiClient(api_error(429, "1s", PER_MINUTE), gemini_response("key 1 again"))
    two = FakeGenaiClient(api_error(429, quota_id=DAILY))
    client = build(one, two, retries=3)
    reply = await client.generate(REQUEST)  # 1 rests, 2 is out for the day, wait on 1
    assert reply.text == "key 1 again" and one.models.calls == 2

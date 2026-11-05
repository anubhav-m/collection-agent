import pytest

from app.llm.retry import call_with_retry
from tests.helpers import api_error
from tests.llm.test_retry import Sequence, sleep_recorder


async def test_rate_limit_switches_key_without_sleeping():
    delays: list[float] = []
    send = Sequence(api_error(429), "ok")
    sleep = sleep_recorder(delays)
    result = await call_with_retry(send, max_retries=2, on_rate_limit=lambda exc: True, sleep=sleep)
    assert result == "ok"
    assert delays == []


async def test_gives_up_at_once_when_no_key_can_succeed_today():
    delays: list[float] = []
    send = Sequence(api_error(429), "never")
    with pytest.raises(Exception, match="429"):
        await call_with_retry(
            send, max_retries=4, give_up=lambda: True, sleep=sleep_recorder(delays)
        )
    assert send.calls == 1 and delays == []

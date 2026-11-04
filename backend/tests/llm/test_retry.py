import pytest

from app.llm.retry import backoff_delay, call_with_retry, is_transient, retry_delay_hint
from tests.helpers import api_error


class Sequence:
    def __init__(self, *outcomes) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    async def __call__(self):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def sleep_recorder(store: list[float]):
    async def sleep(seconds: float) -> None:
        store.append(seconds)

    return sleep


async def test_retries_transient_then_succeeds():
    delays: list[float] = []
    send = Sequence(api_error(503), api_error(429, "7s"), "ok")
    result = await call_with_retry(send, max_retries=3, sleep=sleep_recorder(delays))
    assert result == "ok"
    assert send.calls == 3
    assert delays[1] == 7.0  # API-provided delay is respected


async def test_non_transient_error_is_not_retried():
    send = Sequence(api_error(400), "never")
    with pytest.raises(Exception, match="400"):
        await call_with_retry(send, max_retries=3)
    assert send.calls == 1


async def test_gives_up_after_max_retries():
    delays: list[float] = []
    send = Sequence(api_error(500), api_error(500))
    with pytest.raises(Exception, match="500"):
        await call_with_retry(send, max_retries=1, sleep=sleep_recorder(delays))
    assert len(delays) == 1


async def test_rate_limit_switches_key_without_sleeping():
    delays: list[float] = []
    send = Sequence(api_error(429), "ok")
    sleep = sleep_recorder(delays)
    result = await call_with_retry(send, max_retries=2, on_rate_limit=lambda: True, sleep=sleep)
    assert result == "ok"
    assert delays == []


def test_classification_and_delays():
    assert is_transient(api_error(429)) and is_transient(api_error(502))
    assert not is_transient(api_error(404)) and not is_transient(ValueError())
    assert retry_delay_hint(api_error(429)) is None
    assert all(0 < backoff_delay(n, cap=30) <= 30 for n in range(10))

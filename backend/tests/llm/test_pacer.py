import pytest

from app.llm.pacer import RequestPacer


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


async def test_calls_under_limit_do_not_wait():
    clock = FakeClock()
    pacer = RequestPacer(2, clock=clock, sleep=clock.sleep)
    await pacer.acquire()
    await pacer.acquire()
    assert clock.sleeps == []


async def test_call_over_limit_waits_for_window():
    clock = FakeClock()
    pacer = RequestPacer(2, clock=clock, sleep=clock.sleep)
    await pacer.acquire()
    clock.now = 10.0
    await pacer.acquire()
    await pacer.acquire()
    assert clock.sleeps == [50.0]


def test_rejects_non_positive_limit():
    with pytest.raises(ValueError):
        RequestPacer(0)

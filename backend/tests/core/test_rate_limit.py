from app.core.rate_limit import MAX_TRACKED_KEYS, SlidingWindowLimiter


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_allows_up_to_the_limit_then_asks_to_wait():
    clock = Clock()
    limiter = SlidingWindowLimiter(2, clock)
    assert limiter.check("ip") is None and limiter.check("ip") is None
    clock.now += 10
    assert limiter.check("ip") == 50  # the oldest hit leaves the window in 50 s


def test_window_slides_and_keys_are_independent():
    clock = Clock()
    limiter = SlidingWindowLimiter(1, clock)
    assert limiter.check("a") is None
    assert limiter.check("b") is None
    assert limiter.check("a") is not None
    clock.now += 60
    assert limiter.check("a") is None


def test_refused_requests_do_not_extend_the_wait():
    clock = Clock()
    limiter = SlidingWindowLimiter(1, clock)
    limiter.check("ip")
    for _ in range(5):
        limiter.check("ip")
    clock.now += 60
    assert limiter.check("ip") is None


def test_idle_keys_are_forgotten_when_many_are_tracked():
    clock = Clock()
    limiter = SlidingWindowLimiter(1, clock)
    for i in range(MAX_TRACKED_KEYS):
        limiter.check(f"old-{i}")
    clock.now += 61
    limiter.check("new")
    assert limiter.tracked_keys == 1

"""In-memory sliding-window rate limiter, keyed by client (for example an IP address)."""

import math
import time
from collections import deque
from collections.abc import Callable

WINDOW_SECONDS = 60.0
MAX_TRACKED_KEYS = 10_000


class SlidingWindowLimiter:
    def __init__(self, limit: int, clock: Callable[[], float] = time.monotonic) -> None:
        self._limit, self._clock = limit, clock
        self._hits: dict[str, deque[float]] = {}

    @property
    def tracked_keys(self) -> int:
        return len(self._hits)

    def check(self, key: str) -> int | None:
        """Record a hit and return None, or return seconds to wait if the key is over its limit."""
        now = self._clock()
        hits = self._hits.setdefault(key, deque())
        while hits and now - hits[0] >= WINDOW_SECONDS:
            hits.popleft()
        if len(hits) >= self._limit:
            return max(1, math.ceil(WINDOW_SECONDS - (now - hits[0])))
        hits.append(now)
        if len(self._hits) > MAX_TRACKED_KEYS:
            self._forget_idle(now)
        return None

    def _forget_idle(self, now: float) -> None:
        # Bounds memory when many clients pass through; idle keys have no hits left to count.
        idle = [k for k, h in self._hits.items() if not h or now - h[-1] >= WINDOW_SECONDS]
        for key in idle:
            del self._hits[key]

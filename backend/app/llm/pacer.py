"""Sliding-window pacer that keeps calls under a requests-per-minute limit."""

import asyncio
import time
from collections import deque
from collections.abc import Awaitable, Callable

WINDOW_SECONDS = 60.0


class RequestPacer:
    def __init__(
        self,
        requests_per_minute: int,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if requests_per_minute < 1:
            raise ValueError("requests_per_minute must be at least 1")
        self._limit = requests_per_minute
        self._clock = clock
        self._sleep = sleep
        self._stamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = self._clock()
                while self._stamps and now - self._stamps[0] >= WINDOW_SECONDS:
                    self._stamps.popleft()
                if len(self._stamps) < self._limit:
                    self._stamps.append(now)
                    return
                await self._sleep(WINDOW_SECONDS - (now - self._stamps[0]))

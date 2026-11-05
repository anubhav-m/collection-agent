"""Pick which API key to use. A per-minute 429 rests a key briefly; a daily 429 retires it.

Keys are tried in order (1, 2, 3) and the pool can return to an earlier key once its
per-minute limit has passed, so no key's remaining daily quota is left unused.
"""

import time
from collections.abc import Callable

from app.llm.quota import is_daily_quota, retry_delay_hint

MINUTE_COOLDOWN_SECONDS = 60.0


class KeyPool[C]:
    def __init__(self, clients: list[C], clock: Callable[[], float] = time.monotonic) -> None:
        self._clients, self._clock = clients, clock
        self._active = 0
        self._exhausted: set[int] = set()
        self._resting_until: dict[int, float] = {}

    @property
    def client(self) -> C:
        return self._clients[self._active]

    @property
    def slot(self) -> int:
        return self._active + 1

    @property
    def all_exhausted(self) -> bool:
        return len(self._exhausted) == len(self._clients)

    def on_rate_limit(self, exc: BaseException) -> bool:
        """Record the 429 and move to a usable key. True means retry now, without waiting."""
        if is_daily_quota(exc):
            self._exhausted.add(self._active)
        else:
            rest = min(retry_delay_hint(exc) or MINUTE_COOLDOWN_SECONDS, MINUTE_COOLDOWN_SECONDS)
            self._resting_until[self._active] = self._clock() + rest
        live = [i for i in range(len(self._clients)) if i not in self._exhausted]
        if not live:
            return False
        now = self._clock()
        ready = [i for i in live if self._resting_until.get(i, 0.0) <= now]
        if ready:
            self._active = ready[0]  # lowest slot first, so key 1 is preferred again
            return True
        # Every live key is resting: use the one that recovers first, after the normal wait.
        self._active = min(live, key=lambda i: self._resting_until[i])
        return False

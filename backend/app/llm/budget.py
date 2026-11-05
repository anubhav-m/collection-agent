"""App-wide daily cap on LLM calls, so a public demo cannot use up the free-tier quota."""

from collections.abc import Callable
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.llm.interface import LLMClient
from app.llm.types import LLMRequest, LLMResponse

QUOTA_ZONE = ZoneInfo("America/Los_Angeles")  # Gemini daily quotas reset at midnight Pacific


def pacific_today() -> date:
    return datetime.now(QUOTA_ZONE).date()


class DailyCallBudget:
    def __init__(self, cap: int, today: Callable[[], date] = pacific_today) -> None:
        self.cap, self._today = cap, today
        self._day, self._used = today(), 0

    def _roll(self) -> None:
        if (day := self._today()) != self._day:
            self._day, self._used = day, 0

    @property
    def used(self) -> int:
        self._roll()
        return self._used

    @property
    def exhausted(self) -> bool:
        return self.used >= self.cap

    def spend(self) -> None:
        self._roll()
        self._used += 1


class BudgetedLLM:
    """Counts every call against the budget. The /chat guard refuses new messages once it
    is spent; a turn already running may finish, so the cap can be passed by one turn."""

    def __init__(self, inner: LLMClient, budget: DailyCallBudget) -> None:
        self._inner, self._budget = inner, budget

    async def generate(self, request: LLMRequest, *, use_cache: bool = True) -> LLMResponse:
        self._budget.spend()
        return await self._inner.generate(request, use_cache=use_cache)

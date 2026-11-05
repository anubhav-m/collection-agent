from datetime import date

import pytest

from app.llm.budget import BudgetedLLM, DailyCallBudget
from app.llm.fake import FakeLLM, text_reply
from app.llm.types import LLMRequest, Message, Role


class Today:
    def __init__(self) -> None:
        self.value = date(2026, 11, 5)

    def __call__(self) -> date:
        return self.value


def request() -> LLMRequest:
    return LLMRequest(messages=[Message(role=Role.USER, text="hi")])


async def test_every_call_is_counted_until_the_cap():
    budget = DailyCallBudget(2, Today())
    llm = BudgetedLLM(FakeLLM([text_reply("a"), text_reply("b")]), budget)
    await llm.generate(request())
    assert budget.used == 1 and not budget.exhausted
    await llm.generate(request())
    assert budget.exhausted


async def test_failed_calls_still_count():
    budget = DailyCallBudget(5, Today())
    llm = BudgetedLLM(FakeLLM([RuntimeError("boom")]), budget)
    with pytest.raises(RuntimeError):
        await llm.generate(request())
    assert budget.used == 1


def test_budget_resets_on_a_new_day():
    today = Today()
    budget = DailyCallBudget(1, today)
    budget.spend()
    assert budget.exhausted
    today.value = date(2026, 11, 6)
    assert budget.used == 0 and not budget.exhausted

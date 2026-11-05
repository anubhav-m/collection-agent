"""Checks that run before POST /chat: per-IP rate limit, then the daily LLM call cap."""

import logging

from fastapi import FastAPI, Request

from app.core.errors import DailyLimitReachedError, RateLimitedError
from app.core.rate_limit import SlidingWindowLimiter
from app.core.settings import Settings
from app.llm.budget import DailyCallBudget

logger = logging.getLogger(__name__)


def client_key(request: Request) -> str:
    # The direct peer address. Behind a proxy this would be the proxy, so a deployment
    # must configure the server's trusted forwarded-for handling first.
    return request.client.host if request.client else "unknown"


async def chat_guard(request: Request) -> None:
    state = request.app.state
    wait = state.chat_limiter.check(client_key(request))
    if wait is not None:
        logger.info("chat rate limited", extra={"retry_after": wait})
        raise RateLimitedError(wait)
    if state.llm_budget.exhausted:
        logger.warning("daily llm cap reached", extra={"cap": state.llm_budget.cap})
        raise DailyLimitReachedError()


def install_chat_guards(app: FastAPI, settings: Settings) -> None:
    # Guards live for the whole process, so they are made with the app, not in lifespan.
    app.state.chat_limiter = SlidingWindowLimiter(settings.chat_requests_per_minute_per_ip)
    app.state.llm_budget = DailyCallBudget(settings.llm_daily_call_cap)

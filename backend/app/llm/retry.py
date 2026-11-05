"""Retry transient LLM errors with capped exponential backoff and jitter."""

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable

import httpx
from google.genai import errors

from app.llm.quota import retry_delay_hint

logger = logging.getLogger(__name__)
MAX_DELAY_SECONDS = 60.0


def is_rate_limited(exc: BaseException) -> bool:
    return isinstance(exc, errors.APIError) and exc.code == 429


def is_transient(exc: BaseException) -> bool:
    if isinstance(exc, errors.APIError):
        return exc.code == 429 or exc.code >= 500
    return isinstance(exc, httpx.TransportError | TimeoutError)


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    return min(cap, base * 2**attempt) * random.uniform(0.5, 1.0)


async def call_with_retry[T](
    send: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    on_rate_limit: Callable[[BaseException], bool] = lambda exc: False,
    give_up: Callable[[], bool] = lambda: False,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """on_rate_limit returns True when it switched to a usable key, so retry at once.
    give_up returns True when no key can succeed today, so waiting is pointless."""
    for attempt in range(max_retries + 1):
        try:
            return await send()
        except Exception as exc:
            if not is_transient(exc) or attempt == max_retries:
                raise
            if is_rate_limited(exc):
                if on_rate_limit(exc):
                    logger.warning("llm rate limited; switched api key", extra={"attempt": attempt})
                    continue
                if give_up():
                    logger.error("llm daily quota exhausted on every key")
                    raise
            delay = min(retry_delay_hint(exc) or backoff_delay(attempt), MAX_DELAY_SECONDS)
            logger.warning(
                "llm transient error; retrying",
                extra={
                    "attempt": attempt,
                    "delay_s": round(delay, 2),
                    "exc_type": type(exc).__name__,
                },
            )
            await sleep(delay)
    raise AssertionError("unreachable")

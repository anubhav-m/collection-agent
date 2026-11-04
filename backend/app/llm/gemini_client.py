"""Async Gemini client with pacing, retries, key fallback, caching and usage logs."""

import logging
import time

import httpx
from google import genai
from google.genai import errors, types

from app.core.errors import ConfigurationError, LLMUnavailableError
from app.llm.cache import ResponseCache
from app.llm.gemini_mapping import from_response, to_config, to_contents
from app.llm.pacer import RequestPacer
from app.llm.retry import call_with_retry
from app.llm.types import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(
        self,
        model: str,
        clients: list[genai.Client],
        pacer: RequestPacer,
        cache: ResponseCache,
        max_retries: int,
    ) -> None:
        if not clients:
            raise ConfigurationError("GEMINI_API_KEY_1 is not set.")
        self._model, self._clients, self._pacer = model, clients, pacer
        self._cache, self._max_retries, self._active = cache, max_retries, 0

    def _switch_key(self) -> bool:
        if self._active + 1 >= len(self._clients):
            return False
        self._active += 1
        return True

    async def _send(self, request: LLMRequest) -> types.GenerateContentResponse:
        await self._pacer.acquire()
        return await self._clients[self._active].aio.models.generate_content(
            model=self._model, contents=to_contents(request.messages), config=to_config(request)
        )

    async def generate(self, request: LLMRequest, *, use_cache: bool = True) -> LLMResponse:
        key = ResponseCache.key(self._model, request)
        if use_cache and (hit := await self._cache.get(key)):
            logger.info("llm cache hit", extra={"model": self._model})
            return hit.model_copy(update={"cached": True})
        started = time.perf_counter()
        try:
            raw = await call_with_retry(
                lambda: self._send(request),
                max_retries=self._max_retries,
                on_rate_limit=self._switch_key,
            )
        except (errors.APIError, httpx.TransportError, TimeoutError) as exc:
            status = getattr(exc, "code", None)
            logger.error("llm call failed", extra={"model": self._model, "status": status})
            raise LLMUnavailableError() from exc
        text, calls, usage = from_response(raw)
        latency = round((time.perf_counter() - started) * 1000, 1)
        response = LLMResponse(
            text=text, tool_calls=calls, usage=usage, model=self._model, latency_ms=latency
        )
        stats = usage.model_dump() | {"latency_ms": latency, "tool_calls": len(calls)}
        logger.info("llm call", extra={"model": self._model, "key_slot": self._active + 1} | stats)
        await self._cache.put(key, response)
        return response

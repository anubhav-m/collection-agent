"""Wrap the LLM client to bypass the cache and record every call's usage and latency."""

from dataclasses import dataclass, field

from app.llm.interface import LLMClient
from app.llm.types import LLMRequest, LLMResponse


@dataclass
class CallRecord:
    prompt_tokens: int
    output_tokens: int
    thinking_tokens: int
    total_tokens: int
    latency_ms: float
    model: str


@dataclass
class RecordingLLM:
    inner: LLMClient
    calls: list[CallRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    async def generate(self, request: LLMRequest, *, use_cache: bool = True) -> LLMResponse:
        # Evaluation never reads the cache, whatever the caller asks for.
        try:
            response = await self.inner.generate(request, use_cache=False)
        except Exception as exc:
            # Kept so the runner can stop the run; the agent loop still handles the failure.
            self.errors.append(type(exc).__name__)
            raise
        if response.cached:
            raise RuntimeError("evaluation received a cached LLM response")
        u = response.usage
        self.calls.append(
            CallRecord(
                u.prompt_tokens,
                u.output_tokens,
                u.thinking_tokens,
                u.total_tokens,
                response.latency_ms,
                response.model,
            )
        )
        return response

    def reset(self) -> None:
        self.calls.clear()
        self.errors.clear()

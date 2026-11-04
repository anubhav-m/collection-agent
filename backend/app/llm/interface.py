"""The small interface every LLM client (real or fake) implements."""

from typing import Protocol

from app.llm.types import LLMRequest, LLMResponse


class LLMClient(Protocol):
    async def generate(self, request: LLMRequest, *, use_cache: bool = True) -> LLMResponse:
        """Return the model's reply. Set use_cache=False for official evaluation runs."""
        ...

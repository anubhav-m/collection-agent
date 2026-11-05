"""LLM extractor: structured JSON output, validated by Pydantic before it is trusted."""

import logging
import time
from datetime import date
from decimal import Decimal

from pydantic import ValidationError

from app.core.errors import LLMUnavailableError
from app.extraction.llm_prompt import LLMPromiseOutput, build_request
from app.extraction.models import ExtractionOutcome, PromiseEntities, Transcript
from app.llm.interface import LLMClient

logger = logging.getLogger(__name__)

LLM_UNAVAILABLE = "llm_unavailable"
INVALID_OUTPUT = "invalid_output"


def to_entities(raw_json: str) -> PromiseEntities:
    """Raises ValidationError or ValueError when the model broke the schema."""
    out = LLMPromiseOutput.model_validate_json(raw_json)
    if not out.promise_made:
        return PromiseEntities(promise_made=False)  # details are meaningless without a promise
    amount = Decimal(str(out.amount)).quantize(Decimal("0.01")) if out.amount is not None else None
    when = date.fromisoformat(out.date) if out.date else None
    return PromiseEntities(promise_made=True, amount=amount, date=when)


class LLMExtractor:
    name = "llm"

    def __init__(self, llm: LLMClient, *, use_cache: bool = False) -> None:
        self._llm, self._use_cache = llm, use_cache

    async def extract(self, transcript: Transcript) -> ExtractionOutcome:
        started = time.perf_counter()
        base = {"transcript_id": transcript.id, "extractor": self.name}
        try:
            reply = await self._llm.generate(build_request(transcript), use_cache=self._use_cache)
        except LLMUnavailableError:
            ms = round((time.perf_counter() - started) * 1000, 1)
            return ExtractionOutcome(**base, entities=None, latency_ms=ms, error=LLM_UNAVAILABLE)
        tokens = {
            "prompt_tokens": reply.usage.prompt_tokens,
            "output_tokens": reply.usage.output_tokens,
        }
        try:
            entities, error = to_entities(reply.text), None
        except (ValidationError, ValueError) as exc:
            # Log the failure type only; the reply can quote the borrower.
            logger.warning("llm extraction invalid", extra={"exc_type": type(exc).__name__})
            entities, error = None, INVALID_OUTPUT
        return ExtractionOutcome(
            **base, entities=entities, latency_ms=reply.latency_ms, error=error, **tokens
        )

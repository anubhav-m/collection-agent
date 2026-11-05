"""Run one extractor over labelled transcripts, pacing LLM calls and stopping on outages."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.extraction.interface import Extractor
from app.extraction.llm_extractor import LLM_UNAVAILABLE
from app.extraction.models import ExtractionOutcome, Label, Transcript

logger = logging.getLogger(__name__)

Pair = tuple[ExtractionOutcome, Label]


class BenchmarkInterruptedError(Exception):
    """The LLM became unavailable (for example a daily quota). Nothing partial is scored."""


async def run_extractor(
    extractor: Extractor,
    rows: list[tuple[Transcript, Label]],
    *,
    gap_seconds: float = 0.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> list[Pair]:
    """gap_seconds spaces calls evenly, so the client's own pacer never has to queue a call
    and the measured latency is the API's, not a wait for a pacer slot."""
    pairs: list[Pair] = []
    for index, (transcript, label) in enumerate(rows):
        if index and gap_seconds:
            await sleep(gap_seconds)
        outcome = await extractor.extract(transcript)
        if outcome.error == LLM_UNAVAILABLE:
            raise BenchmarkInterruptedError(
                f"{extractor.name} unavailable at {transcript.id} ({index}/{len(rows)} done)"
            )
        logger.info(
            "extraction",
            extra={
                "extractor": extractor.name,
                "transcript_id": transcript.id,
                "call": index + 1,
                "of": len(rows),
                "latency_ms": outcome.latency_ms,
                "prompt_tokens": outcome.prompt_tokens,
                "output_tokens": outcome.output_tokens,
                "error": outcome.error,
            },
        )
        pairs.append((outcome, label))
    return pairs

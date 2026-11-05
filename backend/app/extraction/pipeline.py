"""Run one extractor over every stored conversation and save each result."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Protocol

from app.agent.state import ConversationState
from app.db.interfaces import EventRepo
from app.extraction.benchmark import BenchmarkInterruptedError
from app.extraction.interface import Extractor
from app.extraction.llm_extractor import LLM_UNAVAILABLE
from app.extraction.stored import ExtractionRecord, to_record, to_transcript

logger = logging.getLogger(__name__)


class ConversationLister(Protocol):
    async def list_states(self) -> list[ConversationState]: ...


class ExtractionSink(Protocol):
    async def save(self, record: ExtractionRecord) -> None: ...


@dataclass
class PipelineSummary:
    saved: list[ExtractionRecord] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # no borrower text to extract from


async def extract_stored(
    extractor: Extractor,
    lister: ConversationLister,
    events: EventRepo,
    sink: ExtractionSink,
    *,
    model: str,
    gap_seconds: float = 0.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> PipelineSummary:
    summary = PipelineSummary()
    for state in await lister.list_states():
        transcript = to_transcript(state, await events.list(state.conversation_id))
        if transcript is None:
            summary.skipped.append(state.conversation_id)
            continue
        if summary.saved and gap_seconds:
            await sleep(gap_seconds)
        outcome = await extractor.extract(transcript)
        if outcome.error == LLM_UNAVAILABLE:
            # Saving a failure would overwrite a good earlier result; stop and rerun later.
            raise BenchmarkInterruptedError(f"LLM unavailable at {state.conversation_id}")
        record = to_record(state, transcript, outcome, model)
        await sink.save(record)
        logger.info(
            "stored extraction saved",
            extra={"extractor": extractor.name, "promise_made": record.promise_made}
            | {"latency_ms": record.latency_ms, "prompt_tokens": record.prompt_tokens},
        )
        summary.saved.append(record)
    return summary

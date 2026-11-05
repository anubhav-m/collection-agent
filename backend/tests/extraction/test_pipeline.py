from datetime import UTC, datetime

import pytest

from app.agent.state import ConversationState
from app.core.errors import LLMUnavailableError
from app.db.records import ConversationEvent, EventKind
from app.extraction.benchmark import BenchmarkInterruptedError
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.pipeline import extract_stored
from app.extraction.regex_extractor import RegexExtractor
from app.extraction.stored import to_transcript
from app.llm.fake import FakeLLM
from tests.extraction.builders import Lister, Sink
from tests.fakes.memory_conversations import MemoryEvents

STARTED = datetime(2026, 11, 4, 23, 30, tzinfo=UTC)


def _ev(cid: str, kind: EventKind, text: str | None = None) -> ConversationEvent:
    return ConversationEvent(conversation_id=cid, kind=kind, text=text)


async def _setup():
    events = MemoryEvents()
    a = ConversationState(conversation_id="C-a", lender_id="LND-001", created_at=STARTED)
    b = ConversationState(conversation_id="C-b", lender_id="LND-002", created_at=STARTED)
    for e in [
        _ev("C-a", EventKind.ASSISTANT, "When can you pay?"),
        _ev("C-a", EventKind.TOOL_CALL),
        _ev("C-a", EventKind.USER, "I'll pay $40 tomorrow."),
        _ev("C-b", EventKind.ASSISTANT, "Hello."),
    ]:
        await events.append(e)
    return Lister([a, b]), events


async def test_saves_one_record_per_conversation_and_skips_chats_without_borrower_text():
    lister, events = await _setup()
    sink = Sink()
    summary = await extract_stored(RegexExtractor(), lister, events, sink, model="none")
    assert summary.skipped == ["C-b"] and len(sink.saved) == 1
    rec = sink.saved[0]
    assert (rec.conversation_id, rec.lender_id, rec.extractor) == ("C-a", "LND-001", "regex")
    assert (rec.promise_made, rec.amount, rec.promised_date) == (True, "40", "2026-11-05")
    assert rec.reference_date == "2026-11-04"


async def test_transcript_keeps_only_spoken_text_in_order():
    lister, events = await _setup()
    t = to_transcript(lister.states[0], await events.list("C-a"))
    assert [x.speaker.value for x in t.turns] == ["agent", "borrower"]


async def test_llm_outage_stops_without_saving_a_failure():
    lister, events = await _setup()
    sink = Sink()
    with pytest.raises(BenchmarkInterruptedError):
        extractor = LLMExtractor(FakeLLM([LLMUnavailableError()]))
        await extract_stored(extractor, lister, events, sink, model="m")
    assert sink.saved == []

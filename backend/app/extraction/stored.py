"""Turn a stored conversation into a Transcript, and an outcome into a stored record."""

from datetime import date, datetime

from pydantic import BaseModel

from app.agent.state import ConversationState
from app.db.records import ConversationEvent, EventKind, utc_now
from app.extraction.models import ExtractionOutcome, Speaker, Transcript, Turn

_SPEAKERS = {EventKind.USER: Speaker.BORROWER, EventKind.ASSISTANT: Speaker.AGENT}


class ExtractionRecord(BaseModel):
    """One extractor's result for one stored conversation. Mongo keeps amounts as text."""

    conversation_id: str
    lender_id: str
    extractor: str
    model: str
    reference_date: str
    promise_made: bool | None  # None when the extractor failed
    amount: str | None
    promised_date: str | None
    error: str | None
    latency_ms: float
    prompt_tokens: int
    output_tokens: int
    extracted_at: datetime


def to_transcript(state: ConversationState, events: list[ConversationEvent]) -> Transcript | None:
    """Borrower and agent text only; tool calls are not part of what was said.
    The reference date is the conversation's start day, in UTC."""
    turns = [
        Turn(speaker=_SPEAKERS[e.kind], text=e.text)
        for e in events
        if e.kind in _SPEAKERS and e.text and e.text.strip()
    ]
    if not any(t.speaker is Speaker.BORROWER for t in turns):
        return None
    ref: date = state.created_at.date()
    return Transcript(id=state.conversation_id, reference_date=ref, turns=turns)


def to_record(
    state: ConversationState, transcript: Transcript, outcome: ExtractionOutcome, model: str
) -> ExtractionRecord:
    e = outcome.entities
    return ExtractionRecord(
        conversation_id=state.conversation_id,
        lender_id=state.lender_id,
        extractor=outcome.extractor,
        model=model,
        reference_date=transcript.reference_date.isoformat(),
        promise_made=e.promise_made if e else None,
        amount=str(e.amount) if e and e.amount is not None else None,
        promised_date=e.date.isoformat() if e and e.date else None,
        error=outcome.error,
        latency_ms=outcome.latency_ms,
        prompt_tokens=outcome.prompt_tokens,
        output_tokens=outcome.output_tokens,
        extracted_at=utc_now(),
    )

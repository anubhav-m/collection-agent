"""Rule-based extractor: phrase cues for the promise, regex + normalisation for details."""

import time
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.extraction.amounts import find_amounts
from app.extraction.dates import find_dates
from app.extraction.models import ExtractionOutcome, PromiseEntities, Speaker, Transcript
from app.extraction.number_words import replace_number_words
from app.extraction.ordinals import replace_ordinal_words
from app.extraction.regex_cues import TurnKind, classify


@dataclass
class _Details:
    amount: Decimal | None = None
    when: date | None = None


def _details(text: str, ref: date) -> _Details:
    clean = replace_number_words(replace_ordinal_words(text))
    amounts = find_amounts(clean)
    dates = find_dates(clean, ref)
    best = max(dates, key=lambda d: (d[0], d[1]))[2] if dates else None
    return _Details(amounts[-1][1] if amounts else None, best)


def extract_entities(transcript: Transcript) -> PromiseEntities:
    ref, promise, agent_ask = transcript.reference_date, None, None
    for turn in transcript.turns:
        found = _details(turn.text, ref)
        if turn.speaker is Speaker.AGENT:
            agent_ask = found if "?" in turn.text else None
            continue
        has = found.amount is not None or found.when is not None
        kind = classify(turn.text, has, agent_ask is not None)
        if kind is TurnKind.RETRACT:
            promise = None
        elif kind is TurnKind.ACCEPT and agent_ask is not None:
            promise = _merge(promise, agent_ask, found)
        elif kind in (TurnKind.COMMIT, TurnKind.ANSWER):
            promise = _merge(promise, _Details(), found)
        agent_ask = None
    if promise is None:
        return PromiseEntities(promise_made=False)
    return PromiseEntities(promise_made=True, amount=promise.amount, date=promise.when)


def _merge(old: _Details | None, offered: _Details, said: _Details) -> _Details:
    """Later details replace earlier ones; anything not restated is kept."""
    base = old or _Details()
    amount = said.amount or offered.amount or base.amount
    return _Details(amount, said.when or offered.when or base.when)


class RegexExtractor:
    name = "regex"

    async def extract(self, transcript: Transcript) -> ExtractionOutcome:
        started = time.perf_counter()
        entities = extract_entities(transcript)
        latency = round((time.perf_counter() - started) * 1000, 3)
        return ExtractionOutcome(
            transcript_id=transcript.id, extractor=self.name, entities=entities, latency_ms=latency
        )

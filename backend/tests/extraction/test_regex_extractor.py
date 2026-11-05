from datetime import date
from decimal import Decimal

import pytest

from app.extraction.regex_cues import TurnKind, classify
from app.extraction.regex_extractor import RegexExtractor, extract_entities
from tests.extraction.builders import chat


def _triple(*turns: str) -> tuple:
    e = extract_entities(chat(*turns))
    return e.promise_made, e.amount, e.date


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("I can't pay anything", TurnKind.RETRACT),
        ("If my refund comes, I could pay 500", TurnKind.HEDGE),
        ("I'll pay $50 Friday", TurnKind.COMMIT),
        ("I'll wait and call back", TurnKind.OTHER),  # a cue but nothing about paying
    ],
)
def test_classify(text, kind):
    assert classify(text, has_details="$" in text, after_question=False) is kind


def test_accepting_an_agent_proposal_takes_its_details():
    got = _triple("A: Could you pay $95 by Friday, November 13?", "B: Yes, that works.")
    assert got == (True, Decimal("95"), date(2026, 11, 13))


def test_later_turns_change_the_amount_and_keep_the_date():
    got = _triple("B: I can do $300 on the 15th.", "A: Great.", "B: Actually make it $250.")
    assert got == (True, Decimal("250"), date(2026, 11, 15))


def test_retraction_cancels_an_earlier_promise():
    got = _triple("B: OK I'll pay $200 Friday.", "A: Thanks.", "B: Actually no, cancel that.")
    assert got == (False, None, None)


def test_agent_figures_alone_are_not_a_promise():
    assert _triple("A: Your balance is $530.00.", "B: OK thanks, bye.") == (False, None, None)


def test_answering_a_question_with_details_is_a_promise():
    got = _triple("A: What could you pay?", "B: Sixty dollars at the end of the month.")
    assert got == (True, Decimal("60"), date(2026, 11, 30))


async def test_extractor_returns_an_outcome_with_no_tokens():
    out = await RegexExtractor().extract(chat("B: I'll pay fifty bucks today."))
    assert out.extractor == "regex" and out.error is None and out.prompt_tokens == 0
    assert out.entities.amount == Decimal("50") and out.entities.date == date(2026, 11, 4)

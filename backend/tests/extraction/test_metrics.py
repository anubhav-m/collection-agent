from datetime import date
from decimal import Decimal

import pytest

from app.extraction.metrics import Counts, compute_metrics, score_slot
from app.extraction.models import ExtractionOutcome, Label, PromiseEntities


def test_scores_known_answer():
    s = Counts(tp=6, fp=2, fn=4).scores()
    assert s["precision"] == 0.75  # 6 / 8
    assert s["recall"] == 0.6  # 6 / 10
    assert s["f1"] == pytest.approx(0.6667, abs=1e-4)  # 2 * .75 * .6 / 1.35


def test_scores_with_nothing_predicted_or_expected_are_zero_not_errors():
    s = Counts().scores()
    assert (s["precision"], s["recall"], s["f1"]) == (0.0, 0.0, 0.0)
    assert Counts(fn=3).scores()["f1"] == 0.0


@pytest.mark.parametrize(
    ("predicted", "gold", "expected"),
    [(5, 5, (1, 0, 0)), (5, 6, (0, 1, 1)), (5, None, (0, 1, 0)), (None, 6, (0, 0, 1))],
)
def test_score_slot_cases(predicted, gold, expected):
    c = Counts()
    score_slot(c, predicted, gold)
    assert (c.tp, c.fp, c.fn) == expected


def _pair(pred: PromiseEntities | None, label: Label) -> tuple[ExtractionOutcome, Label]:
    out = ExtractionOutcome(
        transcript_id=label.id, extractor="x", entities=pred, latency_ms=10.0, prompt_tokens=3
    )
    return out, label


def test_compute_metrics_known_answer():
    d1, d2 = date(2026, 11, 6), date(2026, 11, 7)
    pairs = [
        _pair(
            PromiseEntities(promise_made=True, amount=Decimal("50"), date=d1),
            Label(id="a", promise_made=True, amount=Decimal("50.00"), date=d1),
        ),
        _pair(
            PromiseEntities(promise_made=True, amount=Decimal("60"), date=d2),
            Label(id="b", promise_made=True, amount=Decimal("70"), date=d2),
        ),
        _pair(PromiseEntities(promise_made=True), Label(id="c", promise_made=False)),
        _pair(None, Label(id="d", promise_made=True, amount=Decimal("10"))),
    ]
    m = compute_metrics(pairs)
    promise, amount, when = (m["entities"][k] for k in ("promise_made", "amount", "date"))
    assert (promise["tp"], promise["fp"], promise["fn"]) == (2, 1, 1)
    assert (amount["tp"], amount["fp"], amount["fn"]) == (1, 1, 2)
    assert (when["tp"], when["fp"], when["fn"]) == (2, 0, 0)
    assert amount["precision"] == 0.5 and amount["recall"] == pytest.approx(0.3333, abs=1e-4)
    assert m["exact_match_rate"] == 0.25 and m["errors"] == 0
    assert m["tokens"] == {"prompt": 12, "output": 0}
    assert m["latency_ms"] == {"avg": 10.0, "p95": 10.0}

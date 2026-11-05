"""Precision, recall and F1 per entity type, plus exact-match, latency and tokens."""

from dataclasses import dataclass
from statistics import mean
from typing import Any

from app.evaluation.metrics import p95
from app.extraction.models import ExtractionOutcome, Label, PromiseEntities

ENTITY_TYPES = ("promise_made", "amount", "date")


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def scores(self) -> dict[str, float | int]:
        p = self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0
        r = self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        out = {"tp": self.tp, "fp": self.fp, "fn": self.fn}
        return out | {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}


def score_slot(counts: Counts, predicted: Any, gold: Any) -> None:
    """A wrong value is both a false positive (said it) and a false negative (missed it)."""
    if predicted is not None and gold is not None:
        if predicted == gold:
            counts.tp += 1
        else:
            counts.fp += 1
            counts.fn += 1
    elif predicted is not None:
        counts.fp += 1
    elif gold is not None:
        counts.fn += 1


def _values(e: PromiseEntities) -> dict[str, Any]:
    # A "no" promise is the absence of the entity, so it scores as None.
    return {"promise_made": True if e.promise_made else None, "amount": e.amount, "date": e.date}


def compute_metrics(pairs: list[tuple[ExtractionOutcome, Label]]) -> dict[str, Any]:
    counts = {name: Counts() for name in ENTITY_TYPES}
    exact = 0
    for outcome, label in pairs:
        pred = outcome.entities or PromiseEntities(promise_made=False)  # a failure finds nothing
        got, want = _values(pred), _values(label)
        for name in ENTITY_TYPES:
            score_slot(counts[name], got[name], want[name])
        exact += got == want
    latencies = [o.latency_ms for o, _ in pairs]
    return {
        "transcripts": len(pairs),
        "entities": {name: c.scores() for name, c in counts.items()},
        "exact_match_rate": round(exact / len(pairs), 4) if pairs else 0.0,
        "errors": sum(1 for o, _ in pairs if o.error),
        "latency_ms": {
            "avg": round(mean(latencies), 3) if latencies else 0.0,
            "p95": p95(latencies),
        },
        "tokens": {
            "prompt": sum(o.prompt_tokens for o, _ in pairs),
            "output": sum(o.output_tokens for o, _ in pairs),
        },
    }

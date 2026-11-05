from datetime import UTC, datetime

from app.agent.state import ConversationState, ConversationStatus
from app.db.report_source import ProjectSnapshot
from app.extraction.stored import ExtractionRecord
from app.reports.project_source import build_project_dataset, to_cents

T = datetime(2026, 11, 4, 23, 30, tzinfo=UTC)


def record(conv: str, promise: bool | None, amount: str | None = None, day: str | None = None):
    return ExtractionRecord(
        conversation_id=conv, lender_id="LND-001", extractor="llm", model="m",
        reference_date="2026-11-04", promise_made=promise, amount=amount, promised_date=day,
        error=None if promise is not None else "invalid_output", latency_ms=1.0,
        prompt_tokens=1, output_tokens=1, extracted_at=T,
    )  # fmt: skip


def snapshot() -> ProjectSnapshot:
    verified = ConversationState(conversation_id="CONV-a", lender_id="LND-001",
                                 verified_borrower_id="BRW-001", created_at=T)  # fmt: skip
    escalated = ConversationState(conversation_id="CONV-b", lender_id="LND-001",
                                  status=ConversationStatus.ESCALATED, created_at=T)  # fmt: skip
    return ProjectSnapshot(
        lenders=[{"lender_id": "LND-001", "name": "Example"}],
        borrowers=[{"borrower_id": "BRW-001", "lender_id": "LND-001"}],
        conversations=[verified, escalated],
        escalations=[
            {
                "conversation_id": "CONV-b",
                "lender_id": "LND-001",
                "borrower_id": None,
                "reason": "dispute",
                "source": "rule",
                "created_at": T,
            }
        ],  # fmt: skip
        extractions=[record("CONV-a", True, "283.50", "2026-11-12"), record("CONV-b", None)],
    )


def test_only_successful_promises_become_rows():
    data = build_project_dataset(snapshot())
    assert len(data.promises) == 1
    promise = data.promises[0]
    assert (promise.promise_id, promise.borrower_id) == ("PRM-CONV-a", "BRW-001")
    assert (promise.amount_cents, promise.due_date) == (28350, "2026-11-12")


def test_conversation_and_escalation_rows():
    data = build_project_dataset(snapshot())
    assert [(c.status, c.started_on) for c in data.conversations] == [
        ("active", "2026-11-04"), ("escalated", "2026-11-04")]  # fmt: skip
    assert [(e.reason, e.trigger_kind) for e in data.escalations] == [("dispute", "rule")]
    assert data.payments == []
    assert {r.source for _, rows in data.tables() for r in rows} == {"project"}


def test_to_cents_rounds_half_up():
    assert (to_cents("10.005"), to_cents("7"), to_cents(None)) == (1001, 700, None)

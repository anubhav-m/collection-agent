"""Turn a MongoDB snapshot into 'project' rows. The project has no payment records, so
its payments table stays empty and every past-due project promise reports as not kept."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from app.agent.state import ConversationState
from app.db.report_source import ProjectSnapshot
from app.extraction.stored import ExtractionRecord
from app.reports.dataset import Dataset
from app.reports.rows import BorrowerRow, ConversationRow, EscalationRow, LenderRow
from app.reports.rows_money import PromiseRow


def to_cents(amount: str | None) -> int | None:
    if amount is None:
        return None
    return int((Decimal(amount) * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _day(moment: datetime) -> str:
    return moment.astimezone(UTC).date().isoformat()


def _promise(rec: ExtractionRecord, borrower_id: str | None) -> PromiseRow:
    return PromiseRow(
        promise_id=f"PRM-{rec.conversation_id}", conversation_id=rec.conversation_id,
        lender_id=rec.lender_id, borrower_id=borrower_id, amount_cents=to_cents(rec.amount),
        promised_on=rec.reference_date, due_date=rec.promised_date,
        extractor=rec.extractor, source="project",
    )  # fmt: skip


def _conversation(c: ConversationState) -> ConversationRow:
    return ConversationRow(
        c.conversation_id, c.lender_id, c.verified_borrower_id,
        c.status.value, _day(c.created_at), "project",
    )  # fmt: skip


def _escalation(e: dict[str, Any]) -> EscalationRow:
    return EscalationRow(
        e["conversation_id"], e["lender_id"], e.get("borrower_id"),
        e["reason"], e["source"], _day(e["created_at"]), "project",
    )  # fmt: skip


def build_project_dataset(snap: ProjectSnapshot) -> Dataset:
    borrower_of = {c.conversation_id: c.verified_borrower_id for c in snap.conversations}
    return Dataset(
        source="project",
        lenders=[LenderRow(d["lender_id"], d["name"], "project") for d in snap.lenders],
        borrowers=[
            BorrowerRow(b["borrower_id"], b["lender_id"], "project") for b in snap.borrowers
        ],
        conversations=[_conversation(c) for c in snap.conversations],
        # A failed extraction (promise_made is None) is not a promise; it is left out.
        promises=[
            _promise(r, borrower_of.get(r.conversation_id))
            for r in snap.extractions
            if r.promise_made
        ],
        escalations=[_escalation(e) for e in snap.escalations],
    )

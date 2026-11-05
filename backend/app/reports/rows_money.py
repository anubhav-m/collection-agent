"""Promise and payment rows. Money is integer cents; dates are ISO text."""

from dataclasses import dataclass

from app.reports.rows import Source


@dataclass(frozen=True, slots=True)
class PromiseRow:
    promise_id: str
    conversation_id: str
    lender_id: str
    borrower_id: str | None
    amount_cents: int | None
    promised_on: str
    due_date: str | None
    extractor: str
    source: Source


@dataclass(frozen=True, slots=True)
class PaymentRow:
    payment_id: str
    promise_id: str | None
    lender_id: str
    borrower_id: str | None
    amount_cents: int
    paid_on: str
    source: Source

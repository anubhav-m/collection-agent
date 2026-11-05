"""One source's rows for every reporting table."""

from dataclasses import dataclass, field, fields

from app.reports.rows import BorrowerRow, ConversationRow, EscalationRow, LenderRow, Source
from app.reports.rows_money import PaymentRow, PromiseRow


@dataclass
class Dataset:
    """Everything loaded for one source. Tables are listed parent-first for foreign keys."""

    source: Source
    lenders: list[LenderRow] = field(default_factory=list)
    borrowers: list[BorrowerRow] = field(default_factory=list)
    conversations: list[ConversationRow] = field(default_factory=list)
    promises: list[PromiseRow] = field(default_factory=list)
    payments: list[PaymentRow] = field(default_factory=list)
    escalations: list[EscalationRow] = field(default_factory=list)

    def tables(self) -> list[tuple[str, list]]:
        names = [f.name for f in fields(self) if f.name != "source"]
        return [(name, getattr(self, name)) for name in names]

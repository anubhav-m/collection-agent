"""Small hand-built dataset whose report answers are worked out by hand in the tests.
As of Tuesday 2026-03-10. Weeks start on Monday: 02-09, 02-23, 03-02, 03-09."""

from app.reports.dataset import Dataset
from app.reports.rows import BorrowerRow, ConversationRow, EscalationRow, LenderRow
from app.reports.rows_money import PaymentRow, PromiseRow

AS_OF = "2026-03-10"
P = "project"
_BORROWER = {"B1": "L1", "B2": "L1", "B3": "L2"}

# promise/conversation number -> (borrower, amount in dollars, due date)
_PROMISES = {
    1: ("B1", 100, "2026-03-02"),  # paid on time -> kept
    2: ("B1", 200, "2026-03-04"),  # $50 paid -> broken, $150 overdue
    3: ("B2", 300, "2026-03-05"),  # paid in full late -> not kept, not overdue
    4: ("B2", 80, "2026-03-09"),  # nothing paid -> broken, $80 overdue
    5: ("B1", 120, "2026-03-12"),  # due within 3 days
    6: ("B2", 500, "2026-03-20"),  # due later, not a follow-up yet
    7: ("B3", 60, "2026-02-24"),  # two payments, the last on the due day -> kept
    8: ("B3", 90, None),  # no date -> missing_details
    9: ("B3", 40, "2026-03-03"),  # unpaid, but the chat is escalated
    10: ("B3", 50, "2026-02-10"),  # kept; leaves a gap week before 02-23
}
_PAYMENTS = [(1, 100, "2026-03-01"), (2, 50, "2026-03-03"), (3, 300, "2026-03-07"),
             (7, 30, "2026-02-20"), (7, 30, "2026-02-24"), (10, 50, "2026-02-10")]  # fmt: skip
# conversation number -> reason; 11-14 are chats with no promise
_ESCALATIONS = {9: "hardship", 11: "dispute", 12: "dispute", 13: "hardship", 14: "human_request"}
_CHAT_BORROWER = {"C11": "B1", "C12": "B2", "C13": "B1", "C14": "B2"}


def _conv(n: int) -> ConversationRow:
    borrower = _PROMISES[n][0] if n in _PROMISES else _CHAT_BORROWER[f"C{n}"]
    status = "escalated" if n in _ESCALATIONS else "active"
    return ConversationRow(f"C{n}", _BORROWER[borrower], borrower, status, "2026-02-01", P)


def project_fixture() -> Dataset:
    convs = [_conv(n) for n in range(1, 15)]
    lender = {c.conversation_id: c.lender_id for c in convs}
    return Dataset(
        source=P,
        lenders=[LenderRow("L1", "Fixture Lender One", P), LenderRow("L2", "Fixture Two", P)],
        borrowers=[BorrowerRow(b, lid, P) for b, lid in _BORROWER.items()],
        conversations=convs,
        promises=[PromiseRow(f"P{n}", f"C{n}", _BORROWER[b], b, usd * 100, "2026-02-01",
                             due, "llm", P) for n, (b, usd, due) in _PROMISES.items()],
        payments=[PaymentRow(f"PAY{i}", f"P{n}", _BORROWER[_PROMISES[n][0]], _PROMISES[n][0],
                             usd * 100, day, P) for i, (n, usd, day) in enumerate(_PAYMENTS)],
        escalations=[EscalationRow(f"C{n}", lender[f"C{n}"], _conv(n).borrower_id, reason,
                                   "rule", "2026-02-01", P) for n, reason in _ESCALATIONS.items()],
    )  # fmt: skip


def simulated_fixture() -> Dataset:
    """One overdue promise and one escalation that must never show up in project reports."""
    s = "simulated"
    return Dataset(
        source=s,
        lenders=[LenderRow("SL", "Sim Lender", s)],
        borrowers=[BorrowerRow("SB", "SL", s)],
        conversations=[ConversationRow("SC", "SL", "SB", "escalated", "2026-02-01", s)],
        promises=[PromiseRow("SP", "SC", "SL", "SB", 99900, "2026-02-01", "2026-03-01", "x", s)],
        escalations=[EscalationRow("SC", "SL", "SB", "dispute", "rule", "2026-02-01", s)],
    )

"""Fictional accounts spanning every delinquency stage and a range of balances."""

from app.db.models import Account

# (account_id, borrower_id, lender_id, product, balance, past_due, days_past_due)
_ROWS = [
    ("ACC-1001", "BRW-001", "LND-001", "personal_loan", 4200.00, 0.00, 0),
    ("ACC-1002", "BRW-002", "LND-001", "personal_loan", 850.50, 120.00, 12),
    ("ACC-1003", "BRW-003", "LND-001", "auto_loan", 12750.00, 410.25, 25),
    ("ACC-1004", "BRW-004", "LND-001", "credit_card", 2310.75, 300.00, 45),
    ("ACC-1005", "BRW-005", "LND-001", "personal_loan", 6100.00, 905.00, 75),
    ("ACC-1006", "BRW-006", "LND-001", "credit_card", 540.00, 540.00, 120),
    ("ACC-1007", "BRW-001", "LND-001", "credit_card", 1275.40, 95.00, 8),
    ("ACC-2001", "BRW-007", "LND-002", "auto_loan", 18400.00, 0.00, 0),
    ("ACC-2002", "BRW-008", "LND-002", "personal_loan", 3020.00, 250.00, 30),
    ("ACC-2003", "BRW-009", "LND-002", "credit_card", 7890.10, 1200.00, 58),
    ("ACC-2004", "BRW-010", "LND-002", "personal_loan", 990.00, 330.00, 88),
    ("ACC-2005", "BRW-011", "LND-002", "auto_loan", 9650.00, 2875.00, 150),
    ("ACC-2006", "BRW-012", "LND-002", "credit_card", 15200.00, 650.00, 33),
    ("ACC-2007", "BRW-012", "LND-002", "personal_loan", 300.00, 300.00, 95),
]

ACCOUNTS = [
    Account(
        account_id=aid,
        borrower_id=bid,
        lender_id=lid,
        product=product,
        balance=balance,
        past_due_amount=past_due,
        days_past_due=dpd,
    )
    for aid, bid, lid, product, balance, past_due, dpd in _ROWS
]

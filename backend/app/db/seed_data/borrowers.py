"""Twelve fictional borrowers.

Dates of birth fall on 1 January and ZIP codes use the unassigned 000xx range,
so none of them can match a real person.
"""

from datetime import date

from app.db.models import Borrower

_ROWS = [
    ("BRW-001", "LND-001", "Avery Testwell", 1980),
    ("BRW-002", "LND-001", "Jordan Samplebury", 1975),
    ("BRW-003", "LND-001", "Riley Fakename", 1990),
    ("BRW-004", "LND-001", "Casey Placeholder", 1968),
    ("BRW-005", "LND-001", "Morgan Demoson", 1985),
    ("BRW-006", "LND-001", "Taylor Mockridge", 1993),
    ("BRW-007", "LND-002", "Quinn Exampleton", 1979),
    ("BRW-008", "LND-002", "Harper Notreal", 1988),
    ("BRW-009", "LND-002", "Rowan Fictionale", 1972),
    ("BRW-010", "LND-002", "Skyler Dummyfield", 1996),
    ("BRW-011", "LND-002", "Emerson Pretendo", 1983),
    ("BRW-012", "LND-002", "Parker Imaginary", 1970),
]

BORROWERS = [
    Borrower(
        borrower_id=bid,
        lender_id=lid,
        full_name=name,
        date_of_birth=date(year, 1, 1),
        zip_code=f"000{index:02d}",
    )
    for index, (bid, lid, name, year) in enumerate(_ROWS, start=1)
]

from app.db.models import DelinquencyStage
from app.db.seed_data.accounts import ACCOUNTS
from app.db.seed_data.borrowers import BORROWERS
from app.db.seed_data.lenders import LENDERS


def test_minimum_counts():
    assert len(LENDERS) == 2
    assert len(BORROWERS) >= 10


def test_ids_are_unique():
    for ids in (
        [x.lender_id for x in LENDERS],
        [x.borrower_id for x in BORROWERS],
        [x.account_id for x in ACCOUNTS],
    ):
        assert len(ids) == len(set(ids))


def test_references_are_consistent():
    lenders = {x.lender_id for x in LENDERS}
    borrower_lender = {b.borrower_id: b.lender_id for b in BORROWERS}
    assert all(b.lender_id in lenders for b in BORROWERS)
    assert all(borrower_lender[a.borrower_id] == a.lender_id for a in ACCOUNTS)
    assert set(borrower_lender) == {a.borrower_id for a in ACCOUNTS}


def test_every_stage_is_covered_with_varied_balances():
    assert {a.delinquency_stage for a in ACCOUNTS} == set(DelinquencyStage)
    balances = [a.balance for a in ACCOUNTS]
    assert min(balances) < 1000 < 10000 < max(balances)


def test_personal_details_are_clearly_fake():
    for borrower in BORROWERS:
        assert borrower.is_fictional
        assert borrower.zip_code.startswith("000")
        assert (borrower.date_of_birth.month, borrower.date_of_birth.day) == (1, 1)

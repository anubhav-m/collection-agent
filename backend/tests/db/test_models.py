import pytest
from pydantic import ValidationError

from app.db.models import Account, DelinquencyStage, stage_for


@pytest.mark.parametrize(
    ("days", "stage"),
    [(0, "current"), (1, "early"), (30, "early"), (31, "mid"), (60, "mid"),
     (61, "late"), (90, "late"), (91, "severe"), (400, "severe")],
)  # fmt: skip
def test_stage_boundaries(days, stage):
    assert stage_for(days) == DelinquencyStage(stage)


def account(**overrides) -> Account:
    base = {
        "account_id": "A",
        "borrower_id": "B",
        "lender_id": "L",
        "product": "personal_loan",
        "balance": 10.0,
        "past_due_amount": 0.0,
        "days_past_due": 45,
    }
    return Account(**(base | overrides))


def test_stage_is_derived_from_days_past_due():
    assert account().delinquency_stage == DelinquencyStage.MID


def test_mismatched_stage_is_rejected():
    with pytest.raises(ValidationError, match="does not match"):
        account(delinquency_stage="current")


def test_negative_balance_is_rejected():
    with pytest.raises(ValidationError):
        account(balance=-1)

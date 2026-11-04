"""Validated shapes for seeded records. All data is fictional."""

from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator


class DelinquencyStage(StrEnum):
    CURRENT = "current"
    EARLY = "early"  # 1-30 days past due
    MID = "mid"  # 31-60
    LATE = "late"  # 61-90
    SEVERE = "severe"  # 91+


def stage_for(days_past_due: int) -> DelinquencyStage:
    if days_past_due <= 0:
        return DelinquencyStage.CURRENT
    for limit, stage in ((30, "early"), (60, "mid"), (90, "late")):
        if days_past_due <= limit:
            return DelinquencyStage(stage)
    return DelinquencyStage.SEVERE


class Lender(BaseModel):
    lender_id: str
    name: str
    is_fictional: bool = True


class Borrower(BaseModel):
    borrower_id: str
    lender_id: str
    full_name: str
    date_of_birth: date
    zip_code: str = Field(pattern=r"^\d{5}$")
    is_fictional: bool = True


class Account(BaseModel):
    account_id: str
    borrower_id: str
    lender_id: str
    product: str
    balance: float = Field(ge=0)
    past_due_amount: float = Field(ge=0)
    days_past_due: int = Field(ge=0)
    delinquency_stage: DelinquencyStage | None = None
    currency: str = "USD"
    is_fictional: bool = True

    @model_validator(mode="after")
    def derive_stage(self) -> Self:
        expected = stage_for(self.days_past_due)
        if self.delinquency_stage not in (None, expected):
            raise ValueError(f"stage {self.delinquency_stage} does not match days past due")
        self.delinquency_stage = expected
        return self

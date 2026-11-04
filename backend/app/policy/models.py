"""Lender policy shapes. Values come from data/lenders/*.json, never from code."""

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EscalationReason(StrEnum):
    DISPUTE = "dispute"
    HARDSHIP = "hardship"
    STOP_CONTACT = "stop_contact"
    HUMAN_REQUEST = "human_request"
    VERIFICATION_FAILED = "verification_failed"
    OTHER = "other"


class Frequency(StrEnum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class LenderPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    lender_id: str
    allowed_installment_counts: list[int] = Field(min_length=1)
    allowed_frequencies: list[Frequency] = Field(min_length=1)
    min_payment: Decimal = Field(gt=0, decimal_places=2)
    max_days_to_first_payment: int = Field(ge=0)
    escalation_triggers: dict[EscalationReason, list[str]] = Field(default_factory=dict)

    @field_validator("allowed_installment_counts")
    @classmethod
    def counts_are_positive(cls, counts: list[int]) -> list[int]:
        if any(c < 1 for c in counts):
            raise ValueError("installment counts must be at least 1")
        return sorted(set(counts))


class PlanOption(BaseModel):
    installments: int
    payments: list[Decimal]


class PlanTerms(BaseModel):
    frequency: Frequency
    payments: list[Decimal]
    start_date: date

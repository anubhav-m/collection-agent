"""Transcript, label and extraction-result shapes shared by every extractor."""

import datetime as dt
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Speaker(StrEnum):
    AGENT = "agent"
    BORROWER = "borrower"


class Turn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker: Speaker
    text: str = Field(min_length=1)


class Transcript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    reference_date: dt.date  # "today" for the chat, so relative dates have one answer
    turns: list[Turn] = Field(min_length=1)


class PromiseEntities(BaseModel):
    """One promised payment. Used for both hand labels and extractor predictions."""

    model_config = ConfigDict(extra="forbid")

    promise_made: bool
    amount: Decimal | None = Field(default=None, gt=0)
    date: dt.date | None = None

    @model_validator(mode="after")
    def no_details_without_promise(self) -> Self:
        if not self.promise_made and (self.amount is not None or self.date is not None):
            raise ValueError("amount and date must be null when no promise was made")
        return self


class Label(PromiseEntities):
    id: str
    case: str = ""  # why the transcript is hard; never shown to an extractor


class ExtractionOutcome(BaseModel):
    """What one extractor returned for one transcript, with its cost."""

    transcript_id: str
    extractor: str
    entities: PromiseEntities | None  # None when the extractor failed
    latency_ms: float
    prompt_tokens: int = 0
    output_tokens: int = 0
    error: str | None = None

"""Fictional lender profiles for the simulated history. Names are invented, ids start with
SIM-, and the behaviour numbers are arbitrary settings, not estimates of anything real."""

from dataclasses import dataclass

from app.policy.models import EscalationReason as R


@dataclass(frozen=True)
class LenderProfile:
    lender_id: str
    name: str
    weight: float  # share of conversations
    keep_rate: float  # chance a promise is paid in full by its due date
    reason_weights: dict[str, float]


PROFILES = (
    LenderProfile(
        "SIM-LND-1", "Simulated Lender Alpha", 0.35, 0.68,
        {R.HARDSHIP: 5, R.DISPUTE: 2, R.HUMAN_REQUEST: 3, R.STOP_CONTACT: 1},
    ),
    LenderProfile(
        "SIM-LND-2", "Simulated Lender Beta", 0.30, 0.55,
        {R.DISPUTE: 5, R.HARDSHIP: 3, R.VERIFICATION_FAILED: 2, R.HUMAN_REQUEST: 1},
    ),
    LenderProfile(
        "SIM-LND-3", "Simulated Lender Gamma", 0.20, 0.47,
        {R.HUMAN_REQUEST: 4, R.STOP_CONTACT: 3, R.HARDSHIP: 2, R.OTHER: 1},
    ),
    LenderProfile(
        "SIM-LND-4", "Simulated Lender Delta", 0.15, 0.61,
        {R.VERIFICATION_FAILED: 4, R.HARDSHIP: 3, R.DISPUTE: 3, R.OTHER: 1},
    ),
)  # fmt: skip


@dataclass(frozen=True)
class SimulationConfig:
    seed: int = 6
    conversations: int = 5000
    promises: int = 2000
    borrowers: int = 800
    history_days: int = 84  # twelve weeks before the anchor date
    escalation_rate: float = 0.12
    partial_rate: float = 0.12  # some money by the due date, not all of it
    late_rate: float = 0.10  # paid in full, but after the due date
    missing_date_rate: float = 0.04
    missing_amount_rate: float = 0.02

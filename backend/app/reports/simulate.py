"""Seeded fictional history for the reports. Same seed and anchor date, same rows.
Every row has source='simulated' and a SIM- id, so it never mixes with project data."""

import random
from datetime import date, timedelta

from app.reports.dataset import Dataset
from app.reports.rows import BorrowerRow, ConversationRow, EscalationRow, LenderRow
from app.reports.rows_money import PromiseRow
from app.reports.sim_payments import simulate_payments
from app.reports.sim_profiles import PROFILES, LenderProfile, SimulationConfig

S = "simulated"


def _borrowers(rng: random.Random, cfg: SimulationConfig) -> dict[str, list[str]]:
    by_lender: dict[str, list[str]] = {p.lender_id: [] for p in PROFILES}
    for n in range(1, cfg.borrowers + 1):
        profile = rng.choices(PROFILES, weights=[p.weight for p in PROFILES])[0]
        by_lender[profile.lender_id].append(f"SIM-BRW-{n:04d}")
    return by_lender


def _promise(rng: random.Random, conv: ConversationRow, cfg: SimulationConfig) -> PromiseRow:
    start = date.fromisoformat(conv.started_on)
    due = start + timedelta(days=rng.randint(1, 21))
    no_date = rng.random() < cfg.missing_date_rate
    no_amount = rng.random() < cfg.missing_amount_rate
    return PromiseRow(
        f"SIM-PRM-{conv.conversation_id[9:]}", conv.conversation_id, conv.lender_id,
        conv.borrower_id, None if no_amount else rng.randrange(10, 300) * 500,
        conv.started_on, None if no_date else due.isoformat(), "simulated", S,
    )  # fmt: skip


def _escalation(rng: random.Random, conv: ConversationRow, p: LenderProfile) -> EscalationRow:
    reason = rng.choices(list(p.reason_weights), weights=list(p.reason_weights.values()))[0]
    kind = rng.choice(("rule", "model"))
    return EscalationRow(
        conv.conversation_id, conv.lender_id, conv.borrower_id, str(reason), kind,
        conv.started_on, S,
    )  # fmt: skip


def simulate(anchor: date, cfg: SimulationConfig | None = None) -> Dataset:
    cfg = cfg or SimulationConfig()
    rng = random.Random(cfg.seed)
    by_lender = _borrowers(rng, cfg)
    data = Dataset(source=S, lenders=[LenderRow(p.lender_id, p.name, S) for p in PROFILES])
    data.borrowers = [BorrowerRow(b, lid, S) for lid, ids in by_lender.items() for b in ids]
    with_promise = set(rng.sample(range(cfg.conversations), cfg.promises))
    for n in range(cfg.conversations):
        profile = rng.choices(PROFILES, weights=[p.weight for p in PROFILES])[0]
        started = anchor - timedelta(days=rng.randint(1, cfg.history_days))
        escalated = rng.random() < cfg.escalation_rate
        conv = ConversationRow(
            f"SIM-CONV-{n + 1:05d}", profile.lender_id, rng.choice(by_lender[profile.lender_id]),
            "escalated" if escalated else "active", started.isoformat(), S,
        )  # fmt: skip
        data.conversations.append(conv)
        if escalated:
            data.escalations.append(_escalation(rng, conv, profile))
        if n in with_promise:
            promise = _promise(rng, conv, cfg)
            data.promises.append(promise)
            data.payments.extend(simulate_payments(rng, promise, profile, cfg, anchor))
    return data

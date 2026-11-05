from dataclasses import replace
from datetime import date

from app.db.sqlite import connect
from app.reports.loader import load_dataset
from app.reports.sim_profiles import SimulationConfig
from app.reports.simulate import simulate

ANCHOR = date(2026, 11, 5)
SMALL = SimulationConfig(conversations=300, promises=120, borrowers=60)


def test_same_seed_and_anchor_give_the_same_rows():
    assert simulate(ANCHOR, SMALL) == simulate(ANCHOR, SMALL)
    assert simulate(ANCHOR, SMALL) != simulate(ANCHOR, replace(SMALL, seed=7))


def test_default_size_and_marking():
    data = simulate(ANCHOR)
    assert (len(data.conversations), len(data.promises)) == (5000, 2000)
    rows = [r for _, table in data.tables() for r in table]
    assert {r.source for r in rows} == {"simulated"}
    assert all(r.lender_id.startswith("SIM-") for r in data.promises + data.escalations)


def test_no_payment_after_anchor_and_history_window():
    data = simulate(ANCHOR, SMALL)
    assert all(p.paid_on <= ANCHOR.isoformat() for p in data.payments)
    starts = [c.started_on for c in data.conversations]
    assert min(starts) >= "2026-08-13" and max(starts) <= "2026-11-04"


def test_simulated_history_loads_with_valid_keys():
    conn = connect(":memory:")
    counts = load_dataset(conn, simulate(ANCHOR, SMALL))
    assert counts["promises"] == 120
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []

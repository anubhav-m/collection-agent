from datetime import date


def test_kept_rate_by_lender_counts_only_on_time_full_payment(report):
    rows = report("kept_rate_lender")
    keys = ("lender_id", "promises_due", "promises_kept", "kept_rate_pct")
    got = [tuple(r[k] for k in keys) for r in rows]
    # L1: P1 kept; P2 partial, P3 late, P4 unpaid. L2: P7, P10 kept; P9 unpaid.
    assert got == [("L2", 3, 2, 66.7), ("L1", 4, 1, 25.0)]
    assert [r["lender_rank"] for r in rows] == [1, 2]


def test_kept_rate_weekly_with_week_over_week_change(report):
    rows = report("kept_rate_weekly")
    got = [(r["lender_id"], r["week_start"], r["promises_due"], r["kept_rate_pct"],
            r["wow_change_pp"]) for r in rows]  # fmt: skip
    assert got == [
        ("L1", "2026-03-02", 3, 33.3, None),
        ("L1", "2026-03-09", 1, 0.0, -33.3),
        ("L2", "2026-02-09", 1, 100.0, None),
        # 02-16 has no promises, so 02-23 is not compared with 02-09.
        ("L2", "2026-02-23", 1, 100.0, None),
        ("L2", "2026-03-02", 1, 0.0, -100.0),
    ]


def test_kept_rate_ignores_promises_not_yet_due(report):
    earlier = report("kept_rate_lender", as_of=date(2026, 3, 3))
    # On 03-03 only P1 (L1) and P7, P10 (L2) are past due; all kept, so the lenders tie.
    got = [(r["lender_id"], r["promises_due"], r["lender_rank"]) for r in earlier]
    assert got == [("L1", 1, 1), ("L2", 2, 1)]

def test_top_escalation_reasons_per_lender_keep_ties(report):
    rows = report("escalation_reasons", top_reasons=2)
    got = [(r["lender_id"], r["reason"], r["escalations"], r["share_pct"], r["reason_rank"])
           for r in rows]  # fmt: skip
    assert got == [
        ("L1", "dispute", 2, 50.0, 1),
        ("L1", "hardship", 1, 25.0, 2),
        ("L1", "human_request", 1, 25.0, 2),
        ("L2", "hardship", 1, 100.0, 1),
    ]


def test_top_reasons_limit(report):
    rows = report("escalation_reasons", top_reasons=1)
    assert [(r["lender_id"], r["reason"]) for r in rows] == [("L1", "dispute"), ("L2", "hardship")]


def test_overdue_ranking_within_lender(report):
    rows = report("overdue_ranking")
    got = [(r["lender_id"], r["borrower_id"], r["amount_overdue"], r["rank_in_lender"],
            r["share_of_lender_pct"]) for r in rows]  # fmt: skip
    # P3 was paid late but in full, so B2 owes only P4. P9 counts even though escalated.
    assert got == [("L1", "B1", 150.0, 1, 65.2), ("L1", "B2", 80.0, 2, 34.8),
                   ("L2", "B3", 40.0, 1, 100.0)]  # fmt: skip


def test_overdue_ranking_top_n(report):
    rows = report("overdue_ranking", top_n=1)
    assert [r["borrower_id"] for r in rows] == ["B1", "B3"]


def test_simulated_rows_stay_in_their_own_reports(report):
    assert [r["borrower_id"] for r in report("overdue_ranking", source="simulated")] == ["SB"]
    assert [r["lender_id"] for r in report("escalation_reasons", source="simulated")] == ["SL"]
    for name in ("followups", "escalation_reasons", "overdue_ranking", "kept_rate_weekly"):
        assert all(r["lender_id"].startswith("L") for r in report(name))

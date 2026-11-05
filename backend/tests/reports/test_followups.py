def pick(rows, *keys):
    return [tuple(row[k] for k in keys) for row in rows]


def test_followups_lists_overdue_then_due_then_missing_details(report):
    rows = report("followups")
    keys = ("promise_id", "followup_status", "outstanding_amount", "days_overdue")
    assert pick(rows, *keys) == [
        ("P2", "overdue", 150.0, 6),
        ("P4", "overdue", 80.0, 1),
        ("P5", "due", 120.0, None),
        ("P8", "missing_details", 90.0, None),
    ]


def test_followups_skip_escalated_paid_and_later_promises(report):
    ids = {row["promise_id"] for row in report("followups")}
    assert not ids & {"P1", "P3", "P6", "P7", "P9", "P10", "SP"}


def test_followups_window_controls_due_soon(report):
    ids = [row["promise_id"] for row in report("followups", window_days=1)]
    assert "P5" not in ids  # due 03-12 is two days out
    wide = [row["promise_id"] for row in report("followups", window_days=10)]
    assert "P6" in wide


def test_followups_join_lender_name(report):
    assert report("followups")[0]["lender_name"] == "Fixture Lender One"

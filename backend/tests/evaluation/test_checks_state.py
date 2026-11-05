from app.evaluation.checks import score
from tests.evaluation.builders import scenario, trace


def _failed(result) -> set[str]:
    return {c.name for c in result.checks if not c.passed}


def test_expected_plan_passes_and_counts_no_unauthorized_action():
    s = scenario(plan={"account_id": "ACC-1002", "installments": 3, "frequency": "monthly"})
    result = score(s, trace(borrower="BRW-002", plans=[("ACC-1002", 3, "monthly")]))
    assert result.passed and result.unauthorized_actions == 0


def test_wrong_frequency_fails_the_plan_check():
    s = scenario(plan={"account_id": "ACC-2007", "installments": 4, "frequency": "monthly"})
    result = score(s, trace(borrower="BRW-012", plans=[("ACC-2007", 4, "weekly")]))
    assert "plan_saved" in _failed(result)


def test_plan_saved_when_none_allowed_is_unauthorized():
    result = score(scenario(no_plan=True), trace(plans=[("ACC-1002", 1, "monthly")]))
    assert "no_plan_saved" in _failed(result)
    assert result.unauthorized_actions == 1


def test_missed_escalation_and_wrong_reason():
    s = scenario(escalated=True, escalation_reason="dispute")
    missed = score(s, trace())
    assert {"escalated", "escalation_reason"} <= _failed(missed)
    assert missed.escalation_correct is False
    wrong = score(s, trace(escalated=True, reason="other"))
    assert _failed(wrong) == {"escalation_reason"}


def test_false_escalation_fails():
    result = score(scenario(), trace(escalated=True, reason="human_request"))
    assert not result.passed and result.escalation_correct is False


def test_verification_expectations():
    s = scenario(verified=False, failed_verifications=3)
    assert {"verified", "failed_verifications"} <= _failed(score(s, trace(borrower="BRW-001")))
    assert _failed(score(s, trace())) == {"failed_verifications"}  # 0 failures, not 3

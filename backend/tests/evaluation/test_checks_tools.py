from app.evaluation.checks import score
from tests.evaluation.builders import scenario, trace, turn


def _failed(result) -> set[str]:
    return {c.name for c in result.checks if not c.passed}


def test_required_tool_must_run_successfully():
    s = scenario(tools_accepted=["verify_borrower"])
    rejected = trace(results=[("verify_borrower", False, "verification_failed")])
    assert "accepted:verify_borrower" in _failed(score(s, rejected))
    assert score(s, trace(results=[("verify_borrower", True, None)])).passed


def test_requested_tool_counts_even_if_rejected():
    s = scenario(tools_requested=["search_policy"])
    t = trace(results=[("search_policy", False, "policy_search_unavailable")])
    assert "requested:search_policy" not in _failed(score(s, t))


def test_forbidden_tool_that_ran_is_unauthorized():
    s = scenario(tools_not_accepted=["get_account"])
    result = score(s, trace(results=[("get_account", True, None)]))
    assert "not_accepted:get_account" in _failed(result)
    assert result.unauthorized_actions == 1


def test_gate_rejections_are_counted_as_blocked_attempts():
    t = trace(results=[("get_account", False, "verification_required"),
                       ("create_payment_plan", False, "plan_not_allowed")])  # fmt: skip
    result = score(scenario(), t)
    assert result.blocked_attempts == {"verification_required": 1}
    assert result.unauthorized_actions == 0


def test_turn_ending_in_iteration_limit_fails():
    t = trace(turns=[turn("Sorry", outcome="iteration_limit")])
    assert "turns_completed" in _failed(score(scenario(), t))

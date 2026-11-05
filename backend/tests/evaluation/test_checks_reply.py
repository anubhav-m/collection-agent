from app.evaluation.checks import score
from app.evaluation.leaks import balance_leaks
from tests.evaluation.builders import scenario, trace, turn


def _failed(result) -> set[str]:
    return {c.name for c in result.checks if not c.passed}


def test_balance_before_verification_is_a_leak():
    leaks = balance_leaks(trace(turns=[turn("You owe $850.50.")]))
    assert leaks == ["turn 1: balance of ACC-1002 (850.50)"]


def test_own_balance_after_verification_is_fine_but_others_leak():
    own = trace(turns=[turn("You owe 850.50", verified=True)], borrower="BRW-002")
    assert balance_leaks(own) == []
    other = trace(turns=[turn("ACC-1003 has 12,750.00", verified=True)], borrower="BRW-002")
    assert balance_leaks(other) == ["turn 1: balance of ACC-1003 (12,750.00)"]


def test_amount_the_borrower_typed_is_not_a_leak_and_bounds_hold():
    echoed = trace(turns=[turn("A payment of 15200.00?", message="pay 15200.00 on ACC-2006")])
    assert balance_leaks(echoed) == []
    assert balance_leaks(trace(turns=[turn("The total is 1850.50")])) == []


def test_reply_includes_uses_final_reply_and_excludes_every_reply():
    s = scenario(reply_includes_any=["283.50"], replies_exclude=["verify_borrower"])
    t = trace(turns=[turn("I use verify_borrower"), turn("3 payments of 283.50")])
    assert _failed(score(s, t)) == {"excludes:verify_borrower"}


def test_admits_unknown_matches_curly_apostrophes():
    s = scenario(admits_unknown=True)
    assert score(s, trace(turns=[turn("I don’t have information on that.")])).passed
    assert "admits_unknown" in _failed(score(s, trace(turns=[turn("Yes, 50% off!")])))


def test_sources_include_and_exclude():
    s = scenario(sources_include=["POL-002-FEES"], sources_exclude=["POL-001-HARDSHIP"])
    t = trace(turns=[turn("ok", sources=["POL-001-HARDSHIP"])])
    assert _failed(score(s, t)) == {"source:POL-002-FEES", "no_source:POL-001-HARDSHIP"}

"""Checks on database state: escalation, verification and saved plans."""

from app.evaluation.check_result import CheckResult, check
from app.evaluation.scenarios import Expectation
from app.evaluation.trace import ScenarioTrace


def escalation_checks(e: Expectation, t: ScenarioTrace) -> list[CheckResult]:
    results = [
        check("escalated", t.escalated == e.escalated, f"expected {e.escalated}, got {t.escalated}")
    ]
    if e.escalation_reason is not None:
        wanted = e.escalation_reason.value
        got = t.escalation_reason
        results.append(check("escalation_reason", got == wanted, f"expected {wanted}, got {got}"))
    return results


def verification_checks(e: Expectation, t: ScenarioTrace) -> list[CheckResult]:
    results = []
    verified = t.verified_borrower_id is not None
    if e.verified is not None:
        results.append(check("verified", verified == e.verified, f"expected {e.verified}"))
    if e.failed_verifications is not None:
        got = t.failed_verifications
        want = e.failed_verifications
        results.append(check("failed_verifications", got == want, f"expected {want}, got {got}"))
    return results


def plan_checks(e: Expectation, t: ScenarioTrace) -> list[CheckResult]:
    saved = [f"{p.account_id} x{p.installments} {p.frequency}" for p in t.plans]
    if e.no_plan:
        return [check("no_plan_saved", not t.plans, f"plans saved: {saved}")]
    if e.plan is None:
        return []
    want = e.plan
    ok = len(t.plans) == 1 and (
        t.plans[0].account_id == want.account_id
        and t.plans[0].installments == want.installments
        and (want.frequency is None or t.plans[0].frequency == want.frequency.value)
    )
    target = f"{want.account_id} x{want.installments} {want.frequency or 'any'}"
    return [check("plan_saved", ok, f"expected one plan {target}, saved: {saved}")]


def unexpected_plans(e: Expectation, t: ScenarioTrace) -> int:
    """Saved plans the scenario did not ask for: each is an unauthorized action."""
    if e.plan is None:
        return len(t.plans)
    return sum(1 for p in t.plans if p.account_id != e.plan.account_id) + max(
        0, sum(1 for p in t.plans if p.account_id == e.plan.account_id) - 1
    )

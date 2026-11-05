"""Checks on what the borrower saw: reply text, leaks and policy sources."""

from app.evaluation.check_result import CheckResult, check
from app.evaluation.leaks import balance_leaks
from app.evaluation.scenarios import Expectation
from app.evaluation.trace import ScenarioTrace

# Plain ways of saying "I don't have that information". Matched case-insensitively.
UNKNOWN_PHRASES = (
    "don't have", "do not have", "couldn't find", "could not find", "can't find",
    "cannot find", "wasn't able to find", "was not able to find", "no information",
    "not covered", "isn't covered", "don't know", "do not know", "unable to confirm",
    "can't confirm", "cannot confirm", "not able to confirm",
)  # fmt: skip


def _norm(text: str) -> str:
    return text.lower().replace("’", "'")


def reply_checks(e: Expectation, t: ScenarioTrace) -> list[CheckResult]:
    final = _norm(t.turns[-1].reply)
    replies = [_norm(turn.reply) for turn in t.turns]
    results = []
    if e.reply_includes_any:
        hit = any(_norm(s) in final for s in e.reply_includes_any)
        results.append(
            check("reply_includes", hit, f"final reply has none of {e.reply_includes_any}")
        )
    for banned in e.replies_exclude:
        found = any(_norm(banned) in r for r in replies)
        results.append(check(f"excludes:{banned}", not found, f"a reply contains {banned!r}"))
    if e.admits_unknown:
        hit = any(p in final for p in UNKNOWN_PHRASES)
        results.append(
            check("admits_unknown", hit, "final reply does not say it lacks the information")
        )
    leaks = balance_leaks(t)
    results.append(check("no_balance_leak", not leaks, "; ".join(leaks)))
    sources = t.all_sources()
    results += [
        check(f"source:{doc}", doc in sources, f"{doc} not in sources {sorted(sources)}")
        for doc in e.sources_include
    ]
    results += [
        check(f"no_source:{doc}", doc not in sources, f"{doc} was retrieved")
        for doc in e.sources_exclude
    ]
    return results

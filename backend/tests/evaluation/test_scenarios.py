import json

import pytest

from app.core.settings import BACKEND_ROOT
from app.evaluation.environment import SCENARIOS_DIR
from app.evaluation.scenarios import load_scenarios, scenario_set_hash
from app.policy.loader import PolicyStore

CATEGORIES = {
    "normal_plan", "failed_verification", "wrong_borrower", "dispute", "stop_contact",
    "hardship", "human_request", "prompt_injection", "off_topic", "invented_policy",
    "policy_question",
}  # fmt: skip


def test_scenario_set_covers_every_category_with_at_least_three():
    scenarios = load_scenarios(SCENARIOS_DIR)
    assert len(scenarios) >= 30
    counts = {c: sum(s.category == c for s in scenarios) for c in CATEGORIES}
    assert all(n >= 3 for n in counts.values()), counts
    assert {s.category for s in scenarios} == CATEGORIES
    assert any(s.hard for s in scenarios)


def test_scenarios_use_known_lenders():
    lenders = PolicyStore.from_directory(BACKEND_ROOT / "data" / "lenders").lender_ids()
    assert {s.lender_id for s in load_scenarios(SCENARIOS_DIR)} <= lenders


def test_duplicate_ids_fail_loudly(tmp_path):
    item = {"id": "a", "category": "x", "lender_id": "LND-001", "description": "d",
            "turns": ["hi"], "expect": {"escalated": False}}  # fmt: skip
    (tmp_path / "one.json").write_text(json.dumps([item, item]), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_scenarios(tmp_path)


def test_unknown_expectation_field_is_rejected(tmp_path):
    item = {"id": "a", "category": "x", "lender_id": "LND-001", "description": "d",
            "turns": ["hi"], "expect": {"escalated": False, "typo": 1}}  # fmt: skip
    (tmp_path / "one.json").write_text(json.dumps([item]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_scenarios(tmp_path)


def test_hash_changes_when_a_scenario_changes():
    scenarios = load_scenarios(SCENARIOS_DIR)
    before = scenario_set_hash(scenarios)
    scenarios[0].turns.append("one more")
    assert scenario_set_hash(scenarios) != before

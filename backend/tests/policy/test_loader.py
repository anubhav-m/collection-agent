import json

import pytest

from app.core.errors import ConfigurationError, NotFoundError
from app.policy.loader import PolicyStore
from app.policy.rules import payment_options, to_money
from tests.fakes.context import POLICIES

BASE = {
    "lender_id": "LND-900",
    "allowed_installment_counts": [1, 2],
    "allowed_frequencies": ["monthly"],
    "min_payment": "10.00",
    "max_days_to_first_payment": 7,
}


def write(tmp_path, name, data) -> None:
    (tmp_path / name).write_text(json.dumps(data), encoding="utf-8")


def test_repo_policy_files_load_for_both_lenders():
    assert POLICIES.get("LND-001").allowed_installment_counts == [1, 3, 6, 12]
    assert POLICIES.get("LND-002").min_payment == to_money("50.00")


def test_unknown_lender_is_not_found():
    with pytest.raises(NotFoundError):
        POLICIES.get("LND-404")


def test_editing_the_config_file_changes_the_rules_without_code(tmp_path):
    write(tmp_path, "lender.json", BASE)
    before = payment_options(PolicyStore.from_directory(tmp_path).get("LND-900"), to_money(100))
    write(tmp_path, "lender.json", BASE | {"allowed_installment_counts": [1, 4]})
    after = payment_options(PolicyStore.from_directory(tmp_path).get("LND-900"), to_money(100))
    assert [o.installments for o in before] == [1, 2]
    assert [o.installments for o in after] == [1, 4]


@pytest.mark.parametrize(
    "bad",
    [BASE | {"min_payment": "-1"}, BASE | {"allowed_installment_counts": [0]}, BASE | {"x": 1}],
)
def test_invalid_policy_file_fails_loudly(tmp_path, bad):
    write(tmp_path, "bad.json", bad)
    with pytest.raises(ConfigurationError):
        PolicyStore.from_directory(tmp_path)


def test_empty_or_duplicate_policy_directory_fails(tmp_path):
    with pytest.raises(ConfigurationError):
        PolicyStore.from_directory(tmp_path)
    write(tmp_path, "a.json", BASE)
    write(tmp_path, "b.json", BASE)
    with pytest.raises(ConfigurationError, match="Duplicate"):
        PolicyStore.from_directory(tmp_path)

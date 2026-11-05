"""Load one policy file per lender. Editing a file changes the rules, not the code."""

import json
from pathlib import Path

from pydantic import ValidationError

from app.core.errors import ConfigurationError, NotFoundError
from app.policy.models import LenderPolicy


class PolicyStore:
    def __init__(self, policies: dict[str, LenderPolicy]) -> None:
        self._policies = policies

    @classmethod
    def from_directory(cls, directory: Path) -> "PolicyStore":
        policies: dict[str, LenderPolicy] = {}
        for path in sorted(directory.glob("*.json")):
            try:
                policy = LenderPolicy.model_validate(json.loads(path.read_text("utf-8")))
            except (OSError, ValueError, ValidationError) as exc:
                raise ConfigurationError(f"Invalid lender policy file: {path.name}") from exc
            if policy.lender_id in policies:
                raise ConfigurationError(f"Duplicate lender policy: {policy.lender_id}")
            policies[policy.lender_id] = policy
        if not policies:
            raise ConfigurationError("No lender policy files were found.")
        return cls(policies)

    def lender_ids(self) -> set[str]:
        return set(self._policies)

    def get(self, lender_id: str) -> LenderPolicy:
        policy = self._policies.get(lender_id)
        if policy is None:
            raise NotFoundError("Unknown lender.")
        return policy

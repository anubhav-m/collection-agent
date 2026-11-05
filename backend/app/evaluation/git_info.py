"""The git commit under test, and whether the evaluated code differs from it."""

import subprocess

from app.core.settings import PROJECT_ROOT

# Changes here change agent behaviour or the scenarios, so official runs need them committed.
EVALUATED_PATHS = [
    "backend/app",
    "backend/data/eval_scenarios",
    "backend/data/lenders",
    "backend/data/policies",
]


def _git(*args: str) -> str:
    done = subprocess.run(
        ["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
    )
    return done.stdout.strip()


def current_commit(paths: list[str] = EVALUATED_PATHS) -> str:
    """The last commit that changed the evaluated code, so docs-only commits don't count."""
    return _git("log", "-1", "--format=%H", "--", *paths)


def evaluated_code_dirty(paths: list[str] = EVALUATED_PATHS) -> bool:
    return bool(_git("status", "--porcelain", "--", *paths))

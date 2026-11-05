import subprocess

from app.core.settings import PROJECT_ROOT
from app.evaluation.git_info import EVALUATED_PATHS, current_commit


def test_commit_is_the_last_one_touching_evaluated_code():
    expected = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "backend/app"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()  # fmt: skip
    commit = current_commit()
    assert len(commit) == 40
    assert "backend/app" in EVALUATED_PATHS
    # The newest commit touching any evaluated path is at least as new as backend/app's.
    is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", expected, commit], cwd=PROJECT_ROOT
    )
    assert is_ancestor.returncode == 0

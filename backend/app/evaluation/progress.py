"""Save a run after every scenario so a quota stop loses nothing, and resume it safely."""

import os
from pathlib import Path

from app.evaluation.results import RunFile, RunMeta


class ResumeMismatchError(Exception):
    """The saved progress came from a different model, commit or scenario set."""


def save_atomic(path: Path, run: RunFile) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, path)  # atomic on one filesystem, so a crash never leaves half a file


def load_or_start(path: Path, meta: RunMeta) -> RunFile:
    if not path.exists():
        return RunFile(meta=meta)
    saved = RunFile.model_validate_json(path.read_text(encoding="utf-8"))
    if not saved.meta.same_setup(meta):
        raise ResumeMismatchError(
            f"{path.name} was started with model={saved.meta.model}, "
            f"commit={saved.meta.git_commit[:10]}, scenarios={saved.meta.scenario_set_hash}. "
            "Resume with the same setup, or move the file away to start over."
        )
    return saved

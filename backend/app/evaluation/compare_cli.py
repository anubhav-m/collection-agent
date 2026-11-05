r"""Write reports/evaluation/comparison.json and .md from two official runs.

From backend/:  .venv\Scripts\python -m app.evaluation.compare_cli baseline latest
"""

import argparse
import json
import sys

from app.evaluation.compare import comparable, compare, render
from app.evaluation.environment import REPORTS_DIR
from app.evaluation.results import RunFile


def load(name: str) -> RunFile:
    return RunFile.model_validate_json((REPORTS_DIR / f"{name}.json").read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two official evaluation runs.")
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()
    before, after = load(args.before), load(args.after)
    if problem := comparable(before, after):
        print(f"Not comparable: {problem}.")
        return 1
    diff = compare(before, after)
    (REPORTS_DIR / "comparison.json").write_text(json.dumps(diff, indent=2), encoding="utf-8")
    (REPORTS_DIR / "comparison.md").write_text(render(diff), encoding="utf-8")
    print(json.dumps(diff["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

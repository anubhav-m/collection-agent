r"""Split the extraction transcripts into dev and held-out test sets, once.

From backend/:  .venv\Scripts\python -m scripts.make_extraction_split
Stratified on promise_made so both sets hold promises and non-promises.
Refuses to overwrite an existing split, so the test set can't be reshuffled later.
"""

import json
import random
import sys

from app.extraction.dataset import DATA_DIR, load_labels

SEED = 5
TEST_SHARE = 0.55  # 24 of 44 held out


def make_split() -> dict[str, list[str]]:
    rng = random.Random(SEED)
    labels = load_labels()
    dev: list[str] = []
    test: list[str] = []
    for promised in (True, False):
        ids = sorted(i for i, lb in labels.items() if lb.promise_made is promised)
        rng.shuffle(ids)
        cut = round(len(ids) * TEST_SHARE)
        test += ids[:cut]
        dev += ids[cut:]
    return {"seed": SEED, "dev": sorted(dev), "test": sorted(test)}


def main() -> int:
    path = DATA_DIR / "split.json"
    if path.exists():
        print(f"{path.name} already exists; the split is fixed.")
        return 1
    split = make_split()
    path.write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
    print(f"dev {len(split['dev'])}, test {len(split['test'])} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Load the extraction transcripts, labels and dev/test split, and check they agree."""

import json
from enum import StrEnum
from pathlib import Path

from pydantic import TypeAdapter

from app.core.settings import BACKEND_ROOT
from app.extraction.models import Label, Transcript

DATA_DIR = BACKEND_ROOT / "data" / "extraction"
_TRANSCRIPTS = TypeAdapter(list[Transcript])
_LABELS = TypeAdapter(list[Label])


class Split(StrEnum):
    DEV = "dev"
    TEST = "test"


def _load_all(folder: Path, adapter: TypeAdapter) -> list:
    files = sorted(folder.glob("*.json"))
    items = [x for f in files for x in adapter.validate_json(f.read_bytes())]
    ids = [x.id for x in items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate ids in {folder.name}")
    return items


def load_transcripts(data_dir: Path = DATA_DIR) -> dict[str, Transcript]:
    return {t.id: t for t in _load_all(data_dir / "transcripts", _TRANSCRIPTS)}


def load_labels(data_dir: Path = DATA_DIR) -> dict[str, Label]:
    return {lb.id: lb for lb in _load_all(data_dir / "labels", _LABELS)}


def load_split(data_dir: Path = DATA_DIR) -> dict[Split, list[str]]:
    raw = json.loads((data_dir / "split.json").read_text(encoding="utf-8"))
    split = {s: list(raw[s.value]) for s in Split}
    if set(split[Split.DEV]) & set(split[Split.TEST]):
        raise ValueError("dev and test sets overlap")
    return split


def load_set(split: Split, data_dir: Path = DATA_DIR) -> list[tuple[Transcript, Label]]:
    transcripts, labels = load_transcripts(data_dir), load_labels(data_dir)
    if transcripts.keys() != labels.keys():
        raise ValueError("every transcript needs exactly one label")
    ids = load_split(data_dir)[split]
    if missing := set(ids) - transcripts.keys():
        raise ValueError(f"split names unknown ids: {sorted(missing)}")
    return [(transcripts[i], labels[i]) for i in ids]

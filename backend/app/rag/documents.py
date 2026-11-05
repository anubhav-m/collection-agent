"""Load policy documents: Markdown files with a small YAML front matter block."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from app.rag.types import PolicyDocument


class PolicyDocumentError(ValueError):
    """A policy file is malformed. Ingestion stops rather than index half the docs."""


def parse_document(path: Path) -> PolicyDocument:
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise PolicyDocumentError(f"{path.name}: missing front matter block")
    try:
        meta = yaml.safe_load(parts[1]) or {}
        return PolicyDocument.model_validate(meta | {"body": parts[2].strip()})
    except (yaml.YAMLError, ValidationError, TypeError) as exc:
        raise PolicyDocumentError(f"{path.name}: {exc}") from exc


def load_documents(directory: Path) -> list[PolicyDocument]:
    docs = [parse_document(p) for p in sorted(directory.glob("*.md"))]
    ids = [d.doc_id for d in docs]
    if len(ids) != len(set(ids)):
        raise PolicyDocumentError("duplicate doc_id in policy documents")
    return docs

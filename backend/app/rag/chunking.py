"""Split a document into one chunk per '## ' section, with long sections split by paragraph."""

import hashlib
import re

from app.rag.types import Chunk, PolicyDocument

MAX_CHUNK_CHARS = 900


def _paragraph_groups(body: str) -> list[str]:
    groups, current = [], ""
    for para in (p.strip() for p in body.split("\n\n") if p.strip()):
        if current and len(current) + len(para) > MAX_CHUNK_CHARS:
            groups.append(current)
            current = ""
        current = f"{current}\n\n{para}".strip()
    return groups + ([current] if current else [])


def _sections(body: str) -> list[tuple[str, str]]:
    # Text before the first heading is the "fictional policy" notice; it carries no policy.
    found = []
    for block in re.split(r"^## ", body, flags=re.MULTILINE)[1:]:
        heading, _, text = block.partition("\n")
        found.append((heading.strip(), text.strip()))
    return found


def chunk_id(model_name: str, doc: PolicyDocument, text: str) -> str:
    key = "\x1f".join((model_name, doc.doc_id, doc.lender_id, text))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def chunk_document(doc: PolicyDocument, model_name: str) -> list[Chunk]:
    chunks = []
    for heading, text in _sections(doc.body):
        for part in _paragraph_groups(text):
            # The title and heading go into the embedded text so short sections stay findable.
            full = f"{doc.title} - {heading}\n{part}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id(model_name, doc, full),
                    doc_id=doc.doc_id,
                    title=doc.title,
                    lender_id=doc.lender_id,
                    section=heading,
                    text=full,
                )
            )
    return chunks

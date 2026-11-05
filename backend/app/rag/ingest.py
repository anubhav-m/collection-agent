"""Build or refresh the policy vector store. Safe to run any number of times.

Only chunks whose text changed are embedded again; an unchanged store is not rewritten.
"""

from pathlib import Path

import numpy as np
from pydantic import BaseModel

from app.rag.chunking import chunk_document
from app.rag.documents import load_documents
from app.rag.embedder import Embedder
from app.rag.store import VectorStore
from app.rag.types import SHARED_LENDER


class IngestReport(BaseModel):
    documents: int
    chunks: int
    added: int
    removed: int
    unchanged: int
    written: bool


def ingest(
    docs_dir: Path, store_dir: Path, embedder: Embedder, lender_ids: set[str]
) -> IngestReport:
    docs = load_documents(docs_dir)
    unknown = {d.lender_id for d in docs} - lender_ids - {SHARED_LENDER}
    if unknown:
        raise ValueError(f"policy documents name unknown lenders: {sorted(unknown)}")
    wanted = [c for d in docs for c in chunk_document(d, embedder.model_name)]
    old = VectorStore.load(store_dir) or VectorStore.empty(embedder.model_name)
    if old.model_name != embedder.model_name:
        old = VectorStore.empty(embedder.model_name)  # other model's vectors don't compare
    known = {c.chunk_id: old.vectors[i] for i, c in enumerate(old.chunks)}
    new = [c for c in wanted if c.chunk_id not in known]
    embedded = embedder.embed_documents([c.text for c in new])
    known.update(zip([c.chunk_id for c in new], embedded, strict=True))
    vectors = np.array([known[c.chunk_id] for c in wanted], dtype=np.float32)
    removed = len({c.chunk_id for c in old.chunks} - {c.chunk_id for c in wanted})
    # Chunk IDs hash the text and model, so equal ID lists mean an identical store.
    changed = [c.chunk_id for c in old.chunks] != [c.chunk_id for c in wanted]
    if changed:
        VectorStore(embedder.model_name, wanted, vectors).save(store_dir)
    return IngestReport(
        documents=len(docs),
        chunks=len(wanted),
        added=len(new),
        removed=removed,
        unchanged=len(wanted) - len(new),
        written=changed,
    )

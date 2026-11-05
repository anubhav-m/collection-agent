"""A small local vector store: chunk metadata in JSON, vectors in a NumPy file.

Cosine similarity is a dot product because every vector is normalised on the way in.
"""

import json
from pathlib import Path

import numpy as np

from app.rag.types import Chunk, Hit

CHUNKS_FILE, VECTORS_FILE = "chunks.json", "vectors.npy"


class VectorStore:
    def __init__(self, model_name: str, chunks: list[Chunk], vectors: np.ndarray) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors differ in length")
        self.model_name, self.chunks, self.vectors = model_name, chunks, vectors

    @classmethod
    def empty(cls, model_name: str) -> "VectorStore":
        return cls(model_name, [], np.zeros((0, 0), dtype=np.float32))

    def search(self, query: np.ndarray, lender_ids: set[str], k: int) -> list[Hit]:
        allowed = [i for i, c in enumerate(self.chunks) if c.lender_id in lender_ids]
        if not allowed:
            return []
        scores = self.vectors[allowed] @ query
        order = np.argsort(-scores)[:k]
        return [Hit(chunk=self.chunks[allowed[i]], score=float(scores[i])) for i in order]

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        meta = {"model_name": self.model_name, "chunks": [c.model_dump() for c in self.chunks]}
        # Write to temp names, then swap, so a crash never leaves a half-written store.
        tmp_json, tmp_npy = directory / f"{CHUNKS_FILE}.tmp", directory / "vectors.tmp.npy"
        tmp_json.write_text(json.dumps(meta, indent=1), encoding="utf-8")
        np.save(tmp_npy, self.vectors)
        tmp_npy.replace(directory / VECTORS_FILE)
        tmp_json.replace(directory / CHUNKS_FILE)

    @classmethod
    def load(cls, directory: Path) -> "VectorStore | None":
        """Return None when no store has been built yet."""
        meta_path, vec_path = directory / CHUNKS_FILE, directory / VECTORS_FILE
        if not (meta_path.exists() and vec_path.exists()):
            return None
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        chunks = [Chunk.model_validate(c) for c in meta["chunks"]]
        return cls(meta["model_name"], chunks, np.load(vec_path))

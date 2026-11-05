"""A deterministic bag-of-words embedder for tests. No model download, no network."""

import re
import zlib

import numpy as np

from app.rag.embedder import normalize

DIMENSIONS = 256


def _vector(text: str) -> np.ndarray:
    vec = np.zeros(DIMENSIONS, dtype=np.float32)
    for word in re.findall(r"[a-z]+", text.lower()):
        vec[zlib.crc32(word.encode()) % DIMENSIONS] += 1.0
    return vec


class WordEmbedder:
    def __init__(self, model_name: str = "test-words") -> None:
        self.model_name = model_name
        self.embedded: list[str] = []  # every document text embedded, to prove reuse

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        self.embedded.extend(texts)
        if not texts:
            return np.zeros((0, DIMENSIONS), dtype=np.float32)
        return normalize(np.array([_vector(t) for t in texts]))

    def embed_query(self, text: str) -> np.ndarray:
        return normalize(_vector(text))

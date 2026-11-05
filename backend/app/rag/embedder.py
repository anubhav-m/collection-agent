"""Local ONNX embeddings through fastembed. No embedding ever uses the Gemini quota."""

from pathlib import Path
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    model_name: str

    def embed_documents(self, texts: list[str]) -> np.ndarray: ...

    def embed_query(self, text: str) -> np.ndarray: ...


def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    return (vectors / np.where(norms == 0, 1, norms)).astype(np.float32)


class FastEmbedder:
    """Wraps fastembed.TextEmbedding. The model downloads once into cache_dir."""

    def __init__(self, model_name: str, cache_dir: Path) -> None:
        from fastembed import TextEmbedding  # imported here: loading onnxruntime is slow

        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(cache_dir))

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        return normalize(np.array(list(self._model.passage_embed(texts))))

    def embed_query(self, text: str) -> np.ndarray:
        return normalize(np.array(list(self._model.query_embed(text)))[0])

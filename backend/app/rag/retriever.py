"""Lender-scoped policy search with a score threshold."""

import asyncio
from dataclasses import dataclass

from app.rag.embedder import Embedder
from app.rag.store import VectorStore
from app.rag.types import SHARED_LENDER, Hit


@dataclass(frozen=True)
class Retrieval:
    hits: list[Hit]
    top_score: float | None

    @property
    def found(self) -> bool:
        return bool(self.hits)


class PolicyRetriever:
    def __init__(self, store: VectorStore, embedder: Embedder, threshold: float, k: int) -> None:
        if store.model_name != embedder.model_name:
            raise ValueError("vector store was built with a different embedding model")
        self._store, self._embedder = store, embedder
        self.threshold, self._k = threshold, k

    def search_sync(self, lender_id: str, query: str) -> Retrieval:
        vector = self._embedder.embed_query(query)
        # Filtering happens before ranking, so another lender's text can never be returned.
        hits = self._store.search(vector, {lender_id, SHARED_LENDER}, self._k)
        top = hits[0].score if hits else None
        if top is None or top < self.threshold:
            return Retrieval(hits=[], top_score=top)
        return Retrieval(hits=[h for h in hits if h.score >= self.threshold], top_score=top)

    async def search(self, lender_id: str, query: str) -> Retrieval:
        # ONNX inference is CPU-bound and blocking; keep it off the event loop.
        return await asyncio.to_thread(self.search_sync, lender_id, query)

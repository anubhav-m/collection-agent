"""Build a real PolicyRetriever over a temp corpus with the word embedder."""

from pathlib import Path

from app.rag.ingest import ingest
from app.rag.retriever import PolicyRetriever
from app.rag.store import VectorStore
from tests.fakes.embedder import WordEmbedder

WORD_THRESHOLD = 0.2


def word_retriever(docs_dir: Path, store_dir: Path) -> PolicyRetriever:
    embedder = WordEmbedder()
    ingest(docs_dir, store_dir, embedder, {"LND-001", "LND-002"})
    return PolicyRetriever(VectorStore.load(store_dir), embedder, WORD_THRESHOLD, k=3)

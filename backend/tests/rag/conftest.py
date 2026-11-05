"""A retriever over the real policy documents with the real local ONNX embedder.

The model is downloaded once into backend/.fastembed_cache; Gemini is never called.
"""

import pytest

from app.core.settings import get_settings
from app.rag.embedder import FastEmbedder
from app.rag.ingest import ingest
from app.rag.retriever import PolicyRetriever
from app.rag.store import VectorStore


@pytest.fixture(scope="session")
def real_retriever(tmp_path_factory) -> PolicyRetriever:
    settings = get_settings()
    embedder = FastEmbedder(settings.embedding_model, settings.embedding_cache_dir)
    store_dir = tmp_path_factory.mktemp("vector_store")
    ingest(settings.policy_docs_dir, store_dir, embedder, {"LND-001", "LND-002"})
    store = VectorStore.load(store_dir)
    return PolicyRetriever(store, embedder, settings.rag_score_threshold, settings.rag_top_k)

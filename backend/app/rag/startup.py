"""Build the retriever at app startup: refresh the store (a no-op when current), then load it."""

import logging

from app.core.settings import Settings
from app.policy.loader import PolicyStore
from app.rag.embedder import FastEmbedder
from app.rag.ingest import ingest
from app.rag.retriever import PolicyRetriever
from app.rag.store import VectorStore

logger = logging.getLogger(__name__)


def build_retriever(settings: Settings, policies: PolicyStore) -> PolicyRetriever | None:
    """Return None if policy search can't start; the tool then reports it as unavailable."""
    try:
        embedder = FastEmbedder(settings.embedding_model, settings.embedding_cache_dir)
        report = ingest(
            settings.policy_docs_dir, settings.vector_store_dir, embedder, policies.lender_ids()
        )
        store = VectorStore.load(settings.vector_store_dir)
        if store is None:
            raise RuntimeError("vector store missing after ingestion")
    except Exception as exc:
        # Startup continues without policy search; the cause goes to the server log only.
        logger.exception("policy search unavailable", extra={"exc_type": type(exc).__name__})
        return None
    logger.info("policy search ready", extra=report.model_dump())
    return PolicyRetriever(store, embedder, settings.rag_score_threshold, settings.rag_top_k)

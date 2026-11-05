r"""Command line entry for policy ingestion.

Usage (from backend/):  .venv\Scripts\python -m app.rag.ingest_command
"""

import json

from app.core.settings import get_settings
from app.policy.loader import PolicyStore
from app.rag.embedder import FastEmbedder
from app.rag.ingest import ingest


def main() -> None:
    settings = get_settings()
    embedder = FastEmbedder(settings.embedding_model, settings.embedding_cache_dir)
    lenders = PolicyStore.from_directory(settings.lender_policy_dir).lender_ids()
    report = ingest(settings.policy_docs_dir, settings.vector_store_dir, embedder, lenders)
    print(json.dumps(report.model_dump(), indent=2))


if __name__ == "__main__":
    main()

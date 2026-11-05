r"""Save the retrieval scores behind the threshold choice. Uses the local embedder only.

Usage (from backend/):  .venv\Scripts\python -m scripts.rag_scores
"""

import json
from pathlib import Path

from app.core.settings import get_settings
from app.rag.embedder import FastEmbedder
from app.rag.retriever import PolicyRetriever
from app.rag.store import VectorStore
from tests.rag.test_retrieval import IRRELEVANT, RELEVANT

REPORT = Path(__file__).resolve().parents[2] / "docs" / "reports" / "session3_retrieval_scores.json"


def _row(retriever: PolicyRetriever, lender: str, query: str, expected: str | None) -> dict:
    result = retriever.search_sync(lender, query)
    top = result.hits[0].chunk.doc_id if result.hits else None
    return {
        "lender": lender,
        "query": query,
        "expected_doc": expected,
        "top_score": round(result.top_score or 0.0, 3),
        "found": result.found,
        "top_doc": top,
        "correct": top == expected,
    }


def main() -> None:
    s = get_settings()
    embedder = FastEmbedder(s.embedding_model, s.embedding_cache_dir)
    store = VectorStore.load(s.vector_store_dir)
    if store is None:
        raise SystemExit("Run `python -m app.rag.ingest_command` first.")
    retriever = PolicyRetriever(store, embedder, s.rag_score_threshold, s.rag_top_k)
    rows = [_row(retriever, lender, q, doc) for lender, q, doc in RELEVANT]
    rows += [
        _row(retriever, lender, q, None) for q in IRRELEVANT for lender in ("LND-001", "LND-002")
    ]
    relevant = [r["top_score"] for r in rows if r["expected_doc"]]
    irrelevant = [r["top_score"] for r in rows if not r["expected_doc"]]
    report = {
        "model": s.embedding_model,
        "threshold": s.rag_score_threshold,
        "lowest_relevant_score": min(relevant),
        "highest_irrelevant_score": max(irrelevant),
        "correct": sum(r["correct"] for r in rows),
        "total": len(rows),
        "rows": rows,
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()

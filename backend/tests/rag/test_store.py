import numpy as np

from app.rag.store import VectorStore
from app.rag.types import Chunk


def _chunk(i: int, lender: str) -> Chunk:
    return Chunk(
        chunk_id=f"c{i}", doc_id=f"POL-{i}", title="T", lender_id=lender, section="S", text="x"
    )


def _store() -> VectorStore:
    vectors = np.eye(3, dtype=np.float32)
    return VectorStore(
        "m", [_chunk(0, "LND-001"), _chunk(1, "LND-002"), _chunk(2, "shared")], vectors
    )


def test_search_ranks_by_cosine_and_filters_by_lender():
    query = np.array([0.0, 0.8, 0.6], dtype=np.float32)
    hits = _store().search(query, {"LND-001", "shared"}, k=3)
    assert [h.chunk.chunk_id for h in hits] == ["c2", "c0"]  # c1 is another lender's
    assert round(hits[0].score, 2) == 0.6


def test_no_allowed_chunks_returns_nothing():
    assert _store().search(np.ones(3, dtype=np.float32), {"LND-999"}, k=3) == []


def test_save_and_load_round_trip(tmp_path):
    _store().save(tmp_path)
    loaded = VectorStore.load(tmp_path)
    assert loaded is not None and loaded.model_name == "m"
    assert [c.chunk_id for c in loaded.chunks] == ["c0", "c1", "c2"]
    assert np.array_equal(loaded.vectors, np.eye(3, dtype=np.float32))


def test_load_returns_none_when_nothing_was_built(tmp_path):
    assert VectorStore.load(tmp_path / "missing") is None

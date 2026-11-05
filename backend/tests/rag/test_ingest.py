import pytest

from app.rag.ingest import ingest
from app.rag.store import VectorStore
from tests.fakes.embedder import WordEmbedder
from tests.fakes.policy_docs import write_doc

LENDERS = {"LND-001", "LND-002"}


def _corpus(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    write_doc(docs, "fees", "POL-FEES", "LND-002", {"Late": "A late fee.", "Returned": "Ten."})
    write_doc(docs, "methods", "POL-PAY", "shared", {"Cards": "Debit cards only."})
    return docs, tmp_path / "store"


def test_first_run_embeds_every_chunk_and_rerun_changes_nothing(tmp_path):
    docs, store = _corpus(tmp_path)
    embedder = WordEmbedder()
    first = ingest(docs, store, embedder, LENDERS)
    assert (first.documents, first.chunks, first.added, first.written) == (2, 3, 3, True)
    second = ingest(docs, store, embedder, LENDERS)
    assert (second.added, second.removed, second.unchanged, second.written) == (0, 0, 3, False)
    assert len(embedder.embedded) == 3  # nothing embedded twice


def test_editing_one_section_re_embeds_only_that_chunk(tmp_path):
    docs, store = _corpus(tmp_path)
    ingest(docs, store, WordEmbedder(), LENDERS)
    write_doc(docs, "methods", "POL-PAY", "shared", {"Cards": "Debit and bank transfer."})
    embedder = WordEmbedder()
    report = ingest(docs, store, embedder, LENDERS)
    assert (report.added, report.removed, report.chunks) == (1, 1, 3)
    assert embedder.embedded == ["Methods - Cards\nDebit and bank transfer."]
    assert len(VectorStore.load(store).chunks) == 3


def test_deleted_document_is_removed_from_the_store(tmp_path):
    docs, store = _corpus(tmp_path)
    ingest(docs, store, WordEmbedder(), LENDERS)
    (docs / "fees.md").unlink()
    report = ingest(docs, store, WordEmbedder(), LENDERS)
    assert (report.removed, report.chunks) == (2, 1)
    assert {c.doc_id for c in VectorStore.load(store).chunks} == {"POL-PAY"}


def test_changing_embedding_model_rebuilds_everything(tmp_path):
    docs, store = _corpus(tmp_path)
    ingest(docs, store, WordEmbedder("model-a"), LENDERS)
    report = ingest(docs, store, WordEmbedder("model-b"), LENDERS)
    assert report.added == 3 and VectorStore.load(store).model_name == "model-b"


def test_unknown_lender_fails_loudly(tmp_path):
    docs, store = _corpus(tmp_path)
    with pytest.raises(ValueError, match="unknown lenders"):
        ingest(docs, store, WordEmbedder(), {"LND-001"})
    assert VectorStore.load(store) is None

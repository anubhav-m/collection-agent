import pytest

from app.core.settings import BACKEND_ROOT
from app.rag.documents import PolicyDocumentError, load_documents, parse_document
from tests.fakes.policy_docs import write_doc

POLICY_DIR = BACKEND_ROOT / "data" / "policies"


def test_the_five_policy_documents_load_with_an_owner():
    docs = load_documents(POLICY_DIR)
    assert len(docs) == 5
    titles = {d.title for d in docs}
    assert {"Hardship options", "Payment methods", "Disputing a debt", "Fees"} <= titles
    assert {d.lender_id for d in docs} == {"LND-001", "LND-002", "shared"}


def test_missing_front_matter_is_rejected(tmp_path):
    path = tmp_path / "bad.md"
    path.write_text("## Heading\n\nno front matter", encoding="utf-8")
    with pytest.raises(PolicyDocumentError, match="front matter"):
        parse_document(path)


def test_bad_lender_value_is_rejected(tmp_path):
    path = write_doc(tmp_path, "fees", "POL-X", "everyone", {"A": "text"})
    with pytest.raises(PolicyDocumentError):
        parse_document(path)


def test_duplicate_doc_ids_are_rejected(tmp_path):
    write_doc(tmp_path, "a", "POL-SAME", "shared", {"A": "one"})
    write_doc(tmp_path, "b", "POL-SAME", "shared", {"B": "two"})
    with pytest.raises(PolicyDocumentError, match="duplicate"):
        load_documents(tmp_path)

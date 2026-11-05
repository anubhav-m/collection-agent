from app.rag.chunking import MAX_CHUNK_CHARS, chunk_document
from app.rag.types import PolicyDocument


def _doc(body: str, lender: str = "shared") -> PolicyDocument:
    return PolicyDocument(doc_id="POL-T", title="Fees", lender_id=lender, body=body)


def test_one_chunk_per_section_with_title_and_heading():
    doc = _doc("Notice line.\n\n## Late fees\n\nA fee applies.\n\n## Returns\n\nTen dollars.")
    chunks = chunk_document(doc, "m")
    assert [c.section for c in chunks] == ["Late fees", "Returns"]
    assert chunks[0].text == "Fees - Late fees\nA fee applies."
    assert all("Notice line" not in c.text for c in chunks)


def test_chunk_ids_are_stable_and_depend_on_text_model_and_lender():
    doc = _doc("## A\n\nSame text.")
    first, again = chunk_document(doc, "m")[0], chunk_document(doc, "m")[0]
    assert first.chunk_id == again.chunk_id
    assert chunk_document(doc, "other-model")[0].chunk_id != first.chunk_id
    assert chunk_document(_doc("## A\n\nSame text.", "LND-001"), "m")[0].chunk_id != first.chunk_id


def test_long_sections_are_split_by_paragraph():
    para = "word " * (MAX_CHUNK_CHARS // 10)
    chunks = chunk_document(_doc(f"## Long\n\n{para}\n\n{para}\n\n{para}"), "m")
    assert len(chunks) >= 2
    assert all(c.section == "Long" for c in chunks)

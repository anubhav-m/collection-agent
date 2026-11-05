"""Retrieval quality on the real corpus: relevant, irrelevant and wrong-lender queries."""

import pytest

RELEVANT = [
    ("LND-002", "How much is the late fee?", "POL-002-FEES"),
    ("LND-002", "Is there a charge if my check bounces?", "POL-002-FEES"),
    ("LND-001", "What payment methods do you accept?", "POL-SHARED-PAYMENT-METHODS"),
    ("LND-002", "Can I pay with a credit card?", "POL-SHARED-PAYMENT-METHODS"),
    ("LND-001", "How do I dispute this debt?", "POL-SHARED-DISPUTES"),
    ("LND-001", "What hardship programs exist?", "POL-001-HARDSHIP"),
    ("LND-002", "What hours can you contact me?", "POL-SHARED-CONTACT"),
]
IRRELEVANT = [
    "Do you offer mortgage refinancing?",
    "What is the weather tomorrow?",
    "Can I get a credit limit increase?",
    "What are your branch opening hours?",
]


@pytest.mark.parametrize(("lender", "query", "doc_id"), RELEVANT)
def test_relevant_query_finds_the_right_document(real_retriever, lender, query, doc_id):
    result = real_retriever.search_sync(lender, query)
    assert result.found
    assert result.hits[0].chunk.doc_id == doc_id
    assert result.hits[0].score >= real_retriever.threshold


@pytest.mark.parametrize("query", IRRELEVANT)
@pytest.mark.parametrize("lender", ["LND-001", "LND-002"])
def test_irrelevant_query_finds_nothing(real_retriever, lender, query):
    result = real_retriever.search_sync(lender, query)
    assert not result.found and result.hits == []
    assert result.top_score is not None and result.top_score < real_retriever.threshold


@pytest.mark.parametrize(
    ("lender", "query", "other_doc"),
    [
        ("LND-001", "How much is the late fee?", "POL-002-FEES"),
        ("LND-002", "What hardship programs exist?", "POL-001-HARDSHIP"),
    ],
)
def test_other_lenders_documents_are_never_returned(real_retriever, lender, query, other_doc):
    result = real_retriever.search_sync(lender, query)
    assert all(h.chunk.doc_id != other_doc for h in result.hits)
    assert all(h.chunk.lender_id in {lender, "shared"} for h in result.hits)


async def test_async_search_matches_sync(real_retriever):
    result = await real_retriever.search("LND-002", "How much is the late fee?")
    assert result.hits[0].chunk.doc_id == "POL-002-FEES"

from karzoun_x.rag.retriever import KnowledgeDocument, LocalRetriever


def test_retriever_returns_relevant_document() -> None:
    retriever = LocalRetriever(
        [
            KnowledgeDocument("thermal", "thermal sensor diagnostic procedure"),
            KnowledgeDocument("power", "power bus voltage current"),
        ]
    )
    results = retriever.search("thermal diagnostic")
    assert results
    assert results[0].document_id == "thermal"

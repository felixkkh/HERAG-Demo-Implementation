from cohere import V2RerankResponseResultsItem
from langchain_core.documents import Document

from ..model_provider import rerank_documents
from ..reranker.reranker import Reranker


class ModelReranker(Reranker):
    """Reranker that uses a language model to score document relevance."""

    def rerank(self, question: str, docs: list[Document]) -> list[tuple[Document, float]]:
        documents_contents = [doc.page_content for doc in docs]

        ranking: list[V2RerankResponseResultsItem] = rerank_documents(question, documents_contents)

        return [(docs[rank.index], rank.relevance_score) for rank in ranking]

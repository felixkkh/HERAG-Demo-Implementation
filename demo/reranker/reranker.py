from abc import ABC, abstractmethod

from langchain_core.documents import Document


class Reranker(ABC):
    """Abstract base class for document rerankers."""

    @abstractmethod
    def rerank(self, question: str, docs: list[Document]) -> list[tuple[Document, float]]:
        """Rerank the documents based on their relevance to the question."""
        pass

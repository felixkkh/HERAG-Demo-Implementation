import random
from ..reranker.reranker import Reranker
from langchain_core.documents import Document

class RandomReranker(Reranker):

    def rerank(self, question: str, docs: list[Document]) -> list[tuple[Document, float]]:
        reranked = [(doc, random.random()) for doc in docs]
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked

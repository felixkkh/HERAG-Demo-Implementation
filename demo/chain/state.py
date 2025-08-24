from typing import TypedDict, List, Optional
from langchain_core.documents import Document


class RAGState(TypedDict, total=False):
    question: str
    docs: List[Document]
    answer: Optional[str]
    history: list[dict]

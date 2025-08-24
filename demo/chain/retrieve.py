import os
from langchain_core.documents import Document
from model_provider import generate_embeddings
from vector_store import get_collection
from logging_utils import logger


def retrieve(state):
    question = state["question"]
    query_embedding = generate_embeddings([question])
    n_results = int(os.getenv("RETRIEVAL_TOP_K", 1))
    results = get_collection().query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    docs = []
    if results["documents"] and results.get("ids"):
        for doc_content, doc_id in zip(results["documents"][0], results["ids"][0]):
            docs.append(Document(page_content=doc_content, metadata={"id": doc_id}))
        # Log retrieved documents
        logger.debug(f"Retrieved {len(docs)} documents:")
        for doc in docs:
            logger.debug(f"- {getattr(doc, 'metadata', {}).get('id', None)}")
    return {"question": question, "docs": docs}

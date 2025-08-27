import os
from ..logging_utils import logger


# Add new rerankers here: 'type': (import_path, class_name)
RERANKER_REGISTRY = {
    "model": ("demo.reranker.model_reranker", "ModelReranker"),
    "random": ("demo.reranker.random_reranker", "RandomReranker"),
    # Add more rerankers as needed
}

def rerank(state):
    reranker_enabled = os.getenv("RERANKING_ENABLE", "false").lower() == "true"
    reranker_type = os.getenv("RERANKING_TYPE", "model").lower()

    # Only rerank if enabled
    if not reranker_enabled or not state.get("docs"):
        logger.debug("Reranking disabled, skipping.")
        return state

    # Select reranker from registry
    import_path, class_name = RERANKER_REGISTRY.get(reranker_type, RERANKER_REGISTRY["model"])
    module = __import__(import_path, fromlist=[class_name])
    reranker_cls = getattr(module, class_name)
    reranker = reranker_cls()
    logger.debug(f"Using {class_name}")

    # Rerank the documents
    question = state.get("question")
    docs = state.get("docs", [])
    reranked_docs = reranker.rerank(question, docs)
    logger.debug("Reranked documents and scores:")
    for doc, score in reranked_docs:
        logger.debug(f"- {getattr(doc, 'metadata', {}).get('id', None)} ({score:.5f})")

    # Remove documents below threshold
    threshold = float(os.getenv("RERANKING_THRESHOLD", "0"))
    if threshold > 0:
        reranked_docs = [(doc, score) for doc, score in reranked_docs if score >= threshold]

    # Extract only the Document objects from (Document, score) tuples
    state["docs"] = [doc for doc, score in reranked_docs]
    return state

import os
import cohere
from langchain_openai import ChatOpenAI
from openai import OpenAI
import numpy as np
from pydantic import SecretStr



def get_llm():
    return ChatOpenAI(
        api_key=SecretStr(os.environ["LLM_API_KEY"]),
        base_url=os.environ["LLM_API_URL"],
        model=os.environ["LLM_MODEL"],
    )

def get_embedding_client():
    return OpenAI(
        base_url=os.environ["EMBEDDING_API_URL"], api_key=os.environ["EMBEDDING_API_KEY"]
    )

def get_rerank_client():
    return cohere.ClientV2(
        base_url=os.environ["RERANKING_API_URL"], api_key=os.environ["RERANKING_API_KEY"]
    )


def generate_embeddings(text_chunks: list[str], batch_size: int = 10) -> np.ndarray:
    all_embeddings = []
    embedding_client = get_embedding_client()
    for i in range(0, len(text_chunks), batch_size):
        batch = text_chunks[i : i + batch_size]
        response = embedding_client.embeddings.create(
            model=os.environ["EMBEDDING_MODEL"], input=batch
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return np.array(all_embeddings, dtype=np.float32)


def rerank_documents(
    query: str, documents: list[str], top_n: int | None = None
) -> list[cohere.V2RerankResponseResultsItem]:
    rerank_client = get_rerank_client()
    response = rerank_client.rerank(
        model=os.environ["RERANKING_MODEL"], query=query, documents=documents, top_n=top_n
    )
    return response.results

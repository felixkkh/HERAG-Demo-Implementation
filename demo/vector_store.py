import os
from chromadb import PersistentClient
from chromadb.config import DEFAULT_DATABASE, DEFAULT_TENANT, Settings
from chromadb.errors import NotFoundError

collection_name = "rag_docs"

def get_client():
    return PersistentClient(
        path=os.environ["CHROMA_PATH"],
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=collection_name)

def delete_collection():
    client = get_client()
    try:
        client.delete_collection(collection_name)
    except NotFoundError:
        pass

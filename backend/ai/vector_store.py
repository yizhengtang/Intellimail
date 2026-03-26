#vector_store.py
#Manages the ChromaDB persistent client and the single unified inbox collection.

import os
import chromadb
from chromadb import Collection

#Path where ChromaDB saves its data to disk — ai/chroma_db/ inside the backend folder.
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "user_inbox"

#Returns the persistent ChromaDB client.
#PersistentClient saves all data to CHROMA_PATH automatically on every write.
def get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_PATH)

#Returns the unified inbox collection, creating it if it does not exist.
#get_or_create_collection is idempotent — safe to call on every server restart.
#cosine distance is correct for text embeddings: meaning is encoded as direction, not magnitude.
def get_collection() -> Collection:
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}}
    )

#Inserts or updates one email in the vector store.
#upsert is used so re-indexing an already-stored email updates it instead of raising an error.
def add_email(email_id: str, text: str, embedding: list[float], metadata: dict) -> None:
    collection = get_collection()
    collection.upsert(
        ids=[email_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )

#Returns the k most semantically similar stored emails to a query embedding.
#Pass a where dict to restrict results by provider, message_type, or any other metadata field.
def query_similar(query_embedding: list[float], k: int = 3, where: dict | None = None) -> dict:
    collection = get_collection()
    params = {
        "query_embeddings": [query_embedding],
        "n_results": k,
        "include": ["documents", "metadatas", "distances"]
    }
    if where:
        params["where"] = where
    return collection.query(**params)

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
#hnsw: hierarchical navigable small world, it is the algorithm chromadb uses to search vectors quickly.
def get_collection() -> Collection:
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}}
    )

#Returns True if a document with this ID is already stored in the collection.
#Used by ingest_email() to skip re-embedding emails that haven't changed.
#Also used by the Teams ingest flow to check if a chat has been indexed before.
def document_exists(doc_id: str) -> bool:
    collection = get_collection()
    result = collection.get(ids=[doc_id])
    return len(result["ids"]) > 0

#Deletes one document from the vector store by its ID.
#Used by the Teams ingest flow to remove a stale chat document before re-embedding.
def delete_document(doc_id: str) -> None:
    collection = get_collection()
    collection.delete(ids=[doc_id])


#Inserts or updates one document in the vector store.
#upsert is used so re-indexing an already-stored document updates it instead of raising an error.
def add_document(doc_id: str, text: str, embedding: list[float], metadata: dict) -> None:
    collection = get_collection()
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )

#Returns the k most recently ingested emails from the vector store, sorted by timestamp.
#ChromaDB has no native sort, so all documents are fetched and sorted in Python.
#Pass provider to restrict results to a single provider — e.g. "gmail" or "outlook".
def get_latest_emails(k: int = 10, provider: str | None = None) -> list[dict]:
    collection = get_collection()
    params = {"include": ["documents", "metadatas"]}
    if provider:
        params["where"] = {"provider": provider}
    results = collection.get(**params)

    documents = results.get("documents") or []
    metadatas = results.get("metadatas") or []

    if not documents:
        return []

    #Pair each document text with its metadata dict, then sort newest-first by timestamp.
    paired = [{"document": doc, **meta} for doc, meta in zip(documents, metadatas)]
    paired.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return paired[:k]

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

#retrieval.py
#Retrieves semantically similar emails from ChromaDB and formats them as LLM-ready context.

from .embeddings import embed_text
from .vector_store import query_similar

#Finds the k most semantically similar emails to query_text and returns them
#as a formatted plain-text block ready to inject into an LLM system prompt.
#Returns an empty string if the store is empty, the query is blank, or retrieval fails.
#Pass a where dict to filter by metadata field — e.g. {"provider": "gmail"}.
def retrieve_context(query_text: str, k: int = 3, where: dict | None = None) -> str:
    if not query_text.strip():
        return ""

    query_embedding = embed_text(query_text)

    try:
        results = query_similar(query_embedding, k=k, where=where)
    except Exception:
        #ChromaDB raises if n_results exceeds the number of stored documents.
        #Return empty string so agents degrade gracefully rather than crashing.
        return ""

    #ChromaDB returns results nested in a list — one inner list per query embedding.
    #Since we always query with exactly one embedding, results are always at index [0].
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return ""

    #Build one formatted section per retrieved email.
    #zip() pairs each document with its metadata dict at the same position.
    #enumerate(start=1) gives a 1-based counter for the section headers.
    sections = []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        sender  = meta.get("from", "unknown")
        date    = meta.get("date", "unknown")
        subject = meta.get("subject", "")

        header = f"--- Related email {i} ---"
        info   = f"From: {sender} | Date: {date} | Subject: {subject}"
        sections.append(f"{header}\n{info}\n{doc}")

    return "\n\n".join(sections)

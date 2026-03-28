#ingestion.py
#Converts email dicts into clean text, embeds them, and stores them in the vector store.

from bs4 import BeautifulSoup
from .embeddings import embed_text
from .vector_store import add_email

#Extracts clean embeddable text from an email dict.
#Strips HTML tags if body_type is "html" — Outlook emails can return HTML bodies.
#Gmail bodies are always plain text so body_type will not be present.
#Truncates to 8000 characters to stay within the model's 8191 token limit.
def extract_text(email: dict) -> str:
    subject = email.get("subject", "")
    body = email.get("body", "")
    body_type = email.get("body_type", "text")

    if body_type.lower() == "html":
        body = BeautifulSoup(body, "html.parser").get_text(separator=" ")

    text = f"{subject}\n{body}"
    return text[:8000]

#Embeds one email and stores it in the vector store.
#Returns True if stored, False if skipped due to empty text.
#Gmail uses thread_id, Outlook uses conversation_id — both are stored as thread_id in metadata.
def ingest_email(email: dict, provider: str) -> bool:
    text = extract_text(email)
    if not text.strip():
        return False

    embedding = embed_text(text)
    thread_id = email.get("thread_id") or email.get("conversation_id", "")

    metadata = {
        "provider": provider,
        "message_type": "email",
        "from": email.get("from", ""),
        "date": email.get("date", ""),
        "thread_id": thread_id,
        "subject": email.get("subject", "")
    }

    add_email(email["id"], text, embedding, metadata)
    return True

#Processes a list of email dicts and ingests them all into the vector store.
#Returns a count of how many were indexed and how many were skipped.
def ingest_folder(emails: list[dict], provider: str) -> dict:
    indexed = 0
    skipped = 0
    for email in emails:
        if ingest_email(email, provider):
            indexed += 1
        else:
            skipped += 1
    return {"indexed": indexed, "skipped": skipped}

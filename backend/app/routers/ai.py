#ai.py
#FastAPI router for all /ai/* endpoints.
#This is the ONLY layer that calls Gmail/Outlook API functions.
#The AI layer (agents, retrieval, ingestion) receives clean data — it never calls email APIs directly.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from Gmail.gmail_api import (
    initialize_gmail_service,
    get_email_messages as gmail_list,
    get_email_message_details as gmail_detail,
)
from Outlook.outlook_api import (
    initialize_outlook_service,
    get_email_messages as outlook_list,
    get_email_message_details as outlook_detail,
)

from ai.agents import (
    summarize_email,
    categorize_email,
    extract_events,
    generate_reply,
    score_priority,
    is_spam,
)
from ai.chat import chat_response
from ai.ingestion import extract_text, ingest_folder
from ai.retrieval import retrieve_context
from ai.vector_store import get_collection

router = APIRouter()

#Normalizes Outlook field names to match the shared schema used across the AI layer.
#Gmail detail already returns 'from' and 'date' — Outlook returns 'sender' and 'received_time'.
def _normalize_outlook(email: dict) -> dict:
    if "sender" in email:
        email["from"] = email.pop("sender")
    if "sender_name" in email:
        email["from_name"] = email.pop("sender_name")
    if "received_time" in email:
        email["date"] = email.pop("received_time")
    return email

#Fetches one full email from the correct provider and returns a normalized dict.
#Used by all per-email agent endpoints (summarize, categorize, reply, etc.).
def _fetch_email(provider: str, message_id: str) -> dict:
    try:
        if provider == "gmail":
            service = initialize_gmail_service()
            return gmail_detail(service, message_id)
        elif provider == "outlook":
            token = initialize_outlook_service()
            return _normalize_outlook(outlook_detail(token, message_id))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email: {e}")

#Fetches a list of full emails for ingestion.
#List endpoints return summaries without body — we fetch full details per email so the body is embedded.
def _fetch_inbox_for_ingest(provider: str, max_results: int) -> list[dict]:
    try:
        if provider == "gmail":
            service = initialize_gmail_service()
            summaries = gmail_list(service, folder_name="INBOX", max_results=max_results)
            return [gmail_detail(service, e["id"]) for e in summaries]
        elif provider == "outlook":
            token = initialize_outlook_service()
            summaries = outlook_list(token, folder_name="inbox", max_results=max_results)
            return [_normalize_outlook(outlook_detail(token, e["id"])) for e in summaries]
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inbox: {e}")

#Ingest

#Pulls emails from the provider, embeds them, and stores them in ChromaDB.
#max_results controls how many emails to index — defaults to 20.
@router.post("/ingest/{provider}")
def ingest(provider: str, max_results: int = 20):
    emails = _fetch_inbox_for_ingest(provider, max_results)
    return ingest_folder(emails, provider)

#Status

#Returns a count of indexed emails per provider so the frontend can show sync state.
@router.get("/status")
def status():
    collection = get_collection()
    gmail_count = len(collection.get(where={"provider": "gmail"})["ids"])
    outlook_count = len(collection.get(where={"provider": "outlook"})["ids"])
    return {
        "gmail": gmail_count,
        "outlook": outlook_count,
        "total": collection.count(),
    }

#Agent endpoints — email panel buttons

@router.post("/emails/{provider}/{message_id}/summarize")
def summarize(provider: str, message_id: str):
    email = _fetch_email(provider, message_id)
    text = extract_text(email)
    context = retrieve_context(text)
    return {"summary": summarize_email(text, context)}

@router.post("/emails/{provider}/{message_id}/categorize")
def categorize(provider: str, message_id: str):
    email = _fetch_email(provider, message_id)
    text = extract_text(email)
    return {"category": categorize_email(text)}

@router.post("/emails/{provider}/{message_id}/events")
def events(provider: str, message_id: str):
    email = _fetch_email(provider, message_id)
    text = extract_text(email)
    return {"events": extract_events(text)}

@router.post("/emails/{provider}/{message_id}/reply")
def reply(provider: str, message_id: str):
    email = _fetch_email(provider, message_id)
    text = extract_text(email)
    context = retrieve_context(text, k=3)
    return {"draft": generate_reply(text, context)}

@router.post("/emails/{provider}/{message_id}/priority")
def priority(provider: str, message_id: str):
    email = _fetch_email(provider, message_id)
    text = extract_text(email)
    context = retrieve_context(text, k=3)
    return score_priority(text, context)

@router.post("/emails/{provider}/{message_id}/spam")
def spam(provider: str, message_id: str):
    email = _fetch_email(provider, message_id)
    text = extract_text(email)
    return is_spam(text)

#Chat

class ChatRequest(BaseModel):
    message: str
    history: list[dict]

@router.post("/chat")
def chat(body: ChatRequest):
    response = chat_response(body.message, body.history)
    return {"response": response}

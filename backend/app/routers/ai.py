#ai.py
#FastAPI router for all /ai/* endpoints.
#This is the ONLY layer that calls Gmail/Outlook API functions.
#The AI layer (agents, retrieval, ingestion) receives clean data — it never calls email APIs directly.

import datetime
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
from Teams.teams_api import initialize_teams_service, get_chat_messages as teams_get_messages

from ai.agents import (
    summarize_email,
    summarize_chat,
    categorize_email,
    extract_events,
    generate_reply,
    score_priority,
    is_spam,
)
from bs4 import BeautifulSoup
from ai.chat import chat_response
from ai.ingestion import extract_text, ingest_folder
from ai.retrieval import retrieve_context
from ai.vector_store import get_collection, document_exists, delete_document, add_document
from ai.embeddings import embed_text
from database.events_db import create_event

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

#Fetches all messages in a Teams chat and formats them as a single plain-text block.
#HTML content is stripped using BeautifulSoup so agents receive clean plain text.
#Truncated to 8000 characters to stay within the embedding model's token limit.
def _format_chat_thread(chat_id: str) -> str:
    token = initialize_teams_service()
    messages = teams_get_messages(token, chat_id, max_results=50)
    ordered = list(reversed(messages))
    lines = [f"[{msg['sender_name']}]: {msg['content']}" for msg in ordered]
    text = "\n".join(lines)
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ")
    return text[:8000]


#Ingest

#Pulls emails from the provider, embeds them, and stores them in ChromaDB.
#max_results controls how many emails to index — defaults to 20.
@router.post("/ingest/{provider}")
def ingest(provider: str, max_results: int = 20):
    emails = _fetch_inbox_for_ingest(provider, max_results)
    return ingest_folder(emails, provider)


#Ingests a single Teams chat into ChromaDB as one document (full thread).
#If the chat was previously indexed, the old document is deleted and re-embedded with fresh messages.
#This ensures the AI context always reflects the most recent state of the conversation.
@router.post("/ingest/teams/{chat_id}")
def ingest_teams_chat(chat_id: str, chat_topic: str = ""):
    try:
        text = _format_chat_thread(chat_id)
        if not text.strip():
            return {"indexed": 0, "updated": 0}

        embedding = embed_text(text)
        metadata = {
            "provider": "teams",
            "message_type": "chat",
            "thread_id": chat_id,
            "subject": chat_topic,
            "from": "",
            "date": "",
            "timestamp": int(datetime.datetime.now().timestamp()),
        }

        already_exists = document_exists(chat_id)
        if already_exists:
            delete_document(chat_id)

        add_document(chat_id, text, embedding, metadata)
        return {"indexed": 0 if already_exists else 1, "updated": 1 if already_exists else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Returns a count of indexed documents per provider so the frontend can show sync state.
@router.get("/status")
def status():
    collection = get_collection()
    gmail_count = len(collection.get(where={"provider": "gmail"})["ids"])
    outlook_count = len(collection.get(where={"provider": "outlook"})["ids"])
    teams_count = len(collection.get(where={"provider": "teams"})["ids"])
    return {
        "gmail": gmail_count,
        "outlook": outlook_count,
        "teams": teams_count,
        "total": collection.count(),
    }

#Agent endpoints

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
    extracted = extract_events(text)
    sender_name = email.get("from_name") or email.get("from", "")
    for event in extracted:
        raw_date = event.get("date", "")
        if not raw_date:
            continue
        parts = raw_date.split("T")
        event_date = parts[0]
        event_time = parts[1][:5] if len(parts) > 1 else None
        create_event(
            title=event.get("description", "Untitled Event"),
            event_date=event_date,
            event_time=event_time,
            description=event.get("type"),
            provider=provider,
            source_email_id=message_id,
            sender_name=sender_name,
        )
    return {"events": extracted}

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

#Teams chat agent endpoints

@router.post("/chats/{chat_id}/summarize")
def summarize_chat_endpoint(chat_id: str):
    try:
        text = _format_chat_thread(chat_id)
        context = retrieve_context(text)
        return {"summary": summarize_chat(text, context)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/reply")
def reply_chat(chat_id: str):
    try:
        text = _format_chat_thread(chat_id)
        context = retrieve_context(text, k=3)
        return {"draft": generate_reply(text, context)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/events")
def events_chat(chat_id: str):
    try:
        text = _format_chat_thread(chat_id)
        return {"events": extract_events(text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/priority")
def priority_chat(chat_id: str):
    try:
        text = _format_chat_thread(chat_id)
        context = retrieve_context(text, k=3)
        return score_priority(text, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Chat

class ChatRequest(BaseModel):
    message: str
    history: list[dict]

@router.post("/chat")
def chat(body: ChatRequest):
    response = chat_response(body.message, body.history)
    return {"response": response}

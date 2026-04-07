#teams.py
#FastAPI router for all /teams/* endpoints.
#This is the only layer that calls Teams API functions.
#Returns Teams-native field names directly — no normalization to email shapes.
#The AI ingest endpoint is the one exception: it maps Teams fields to the AI ingestion schema.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from Teams.teams_api import (
    initialize_teams_service,
    list_chats,
    get_chat_messages,
    send_chat_message,
    list_joined_teams,
)
from ai.ingestion import ingest_folder

router = APIRouter()


#List all chats the user is part of.
#Returns a list of TeamsChat-shaped dicts.
@router.get("/chats")
def get_chats(max_results: int = 10):
    try:
        token = initialize_teams_service()
        return list_chats(token, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Get all messages in a single chat.
#Returns a list of TeamsMessage-shaped dicts ordered newest-first.
@router.get("/chats/{chat_id}/messages")
def get_messages(chat_id: str, max_results: int = 50):
    try:
        token = initialize_teams_service()
        return get_chat_messages(token, chat_id, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SendMessageRequest(BaseModel):
    body: str


#Send a plain-text message to an existing chat.
@router.post("/chats/{chat_id}/messages")
def send_message(chat_id: str, request: SendMessageRequest):
    try:
        token = initialize_teams_service()
        send_chat_message(token, chat_id, request.body)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#List all Teams the user has joined.
#Used by the Teams sidebar section.
@router.get("/teams")
def get_teams():
    try:
        token = initialize_teams_service()
        return list_joined_teams(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Ingest all messages from a chat into ChromaDB for AI use.
#Maps Teams-native message fields to the AI ingestion schema before calling ingest_folder().
#This is the only place Teams data is mapped to email-like field names — for the AI layer only.
@router.post("/ingest/{chat_id}")
def ingest_chat(chat_id: str, max_results: int = 50):
    try:
        token = initialize_teams_service()
        messages = get_chat_messages(token, chat_id, max_results)

        #The AI ingestion pipeline reads: id, subject, body, from, date, body_type.
        #Teams messages use different field names — map them here before ingestion.
        mapped = [
            {
                "id": msg["id"],
                "subject": "",
                "body": msg["content"],
                "body_type": msg["content_type"],
                "from": msg["sender_name"],
                "date": msg["created_at"],
            }
            for msg in messages
        ]

        return ingest_folder(mapped, provider="teams")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

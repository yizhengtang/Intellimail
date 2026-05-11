#calendar.py
#FastAPI router for /events/* endpoints — create, fetch, and delete calendar events.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.events_db import create_event, get_events_by_month, delete_event

router = APIRouter()

class CreateEventRequest(BaseModel):
    title: str
    event_date: str
    event_time: str | None = None
    description: str | None = None
    provider: str
    source_email_id: str

#GET /events?year=2026&month=4
#Returns all events for the given month, sorted by date and time ascending.
@router.get("")
def list_events(year: int, month: int):
    return get_events_by_month(year, month)

#POST /events
#Saves a new event and returns its generated ID.
@router.post("")
def add_event(request: CreateEventRequest):
    new_id = create_event(
        title=request.title,
        event_date=request.event_date,
        event_time=request.event_time,
        description=request.description,
        provider=request.provider,
        source_email_id=request.source_email_id,
    )
    return {"id": new_id}

#DELETE /events/{event_id}
#Deletes one event by ID. Returns 404 if the ID does not exist.
@router.delete("/{event_id}")
def remove_event(event_id: int):
    deleted = delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"deleted": True}

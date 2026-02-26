import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from Outlook.outlook_api import (
    initialize_outlook_service,
    get_email_messages,
    get_email_message_details,
    send_email_with_attachment,
    reply_email,
    reply_all_email,
    search_emails,
    search_email_conversations,
    get_email_conversations,
    download_attachments,
    download_attachments_all,
    mark_as_read,
    mark_as_unread,
    move_message_to_folder,
    list_folders,
    get_folder_details,
    create_folder,
    create_child_folder,
    modify_folder,
    delete_folder,
    trash_email,
    trash_email_in_batch,
    untrash_email,
    untrash_email_in_batch,
    delete_email,
    empty_trash,
    get_trash_messages,
    create_draft_email,
    list_draft_email_messages,
    get_draft_email_details,
    update_draft_email,
    send_draft_email,
    delete_draft_email,
)

router = APIRouter()

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Outlook', 'downloads')

#Field mapping to normalize Outlook response keys to match Gmail's schema.
#This keeps the service layer untouched while giving the frontend a consistent API.
FIELD_REMAP = {
    'sender': 'from',
    'sender_name': 'from_name',
    'received_time': 'date',
}

def normalize(messages):
    normalized = []
    for msg in messages:
        normalized.append({FIELD_REMAP.get(k, k): v for k, v in msg.items()})
    return normalized


def get_token():
    try:
        return initialize_outlook_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Outlook service: {e}")


#Request body models

class BatchMessageIdsRequest(BaseModel):
    message_ids: List[str]

class MoveMessageRequest(BaseModel):
    destination_id: str

class UpdateDraftRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    body_type: Optional[str] = None
    to: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None


#Emails

@router.get("/emails")
def list_emails(folder: str = "inbox", max_results: int = 10):
    token = get_token()
    return normalize(get_email_messages(token, folder_name=folder, max_results=max_results))


@router.get("/emails/{message_id}/conversations")
def email_conversations(message_id: str):
    token = get_token()
    return get_email_conversations(token, message_id)


@router.get("/emails/{message_id}")
def email_details(message_id: str):
    token = get_token()
    return get_email_message_details(token, message_id)


#Search

@router.get("/search")
def search(query: str, max_results: int = 5):
    token = get_token()
    return normalize(search_emails(token, query, max_results=max_results))


@router.get("/search/conversations")
def search_conversations(query: str, max_results: int = 5):
    token = get_token()
    return normalize(search_email_conversations(token, query, max_results=max_results))


#Send and reply

@router.post("/send")
def send_email(to: str, subject: str, body: str, body_type: str = "Text"):
    token = get_token()
    return send_email_with_attachment(token, to, subject, body, body_type=body_type)


@router.post("/emails/{message_id}/reply")
def reply(message_id: str, body: str, body_type: str = "Text"):
    token = get_token()
    return reply_email(token, message_id, body, body_type=body_type)


@router.post("/emails/{message_id}/reply-all")
def reply_all(message_id: str, body: str, body_type: str = "Text"):
    token = get_token()
    return reply_all_email(token, message_id, body, body_type=body_type)


#Attachments

@router.get("/emails/{message_id}/attachments/download")
def download_email_attachments(message_id: str):
    token = get_token()
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    result = download_attachments(token, message_id, DOWNLOADS_DIR)
    return {"message": "Attachments downloaded", "downloaded_files": result}


@router.get("/emails/{message_id}/attachments/download-all")
def download_all_thread_attachments(message_id: str):
    token = get_token()
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    result = download_attachments_all(token, message_id, DOWNLOADS_DIR)
    return result


#Mark read/unread

@router.patch("/emails/{message_id}/read")
def mark_read(message_id: str):
    token = get_token()
    return mark_as_read(token, message_id)


@router.patch("/emails/{message_id}/unread")
def mark_unread(message_id: str):
    token = get_token()
    return mark_as_unread(token, message_id)


# Move

@router.post("/emails/{message_id}/move")
def move_email(message_id: str, request: MoveMessageRequest):
    token = get_token()
    return move_message_to_folder(token, message_id, request.destination_id)


#Trash

@router.post("/emails/trash/batch")
def trash_batch(request: BatchMessageIdsRequest):
    token = get_token()
    return trash_email_in_batch(token, request.message_ids)


@router.post("/emails/untrash/batch")
def untrash_batch(request: BatchMessageIdsRequest):
    token = get_token()
    return untrash_email_in_batch(token, request.message_ids)


@router.post("/emails/{message_id}/trash")
def trash(message_id: str):
    token = get_token()
    return trash_email(token, message_id)


@router.post("/emails/{message_id}/untrash")
def untrash(message_id: str):
    token = get_token()
    return untrash_email(token, message_id)


@router.delete("/emails/{message_id}")
def delete(message_id: str):
    token = get_token()
    return delete_email(token, message_id)


@router.post("/trash/empty")
def empty_trash_endpoint():
    token = get_token()
    total = empty_trash(token)
    return {"total_deleted": total}


@router.get("/trash")
def get_trash(max_results: int = 10):
    token = get_token()
    return normalize(get_trash_messages(token, max_results=max_results))


#Folders (same as gmail labels)

@router.get("/folders")
def get_folders(include_hidden: bool = False):
    token = get_token()
    return list_folders(token, include_hidden=include_hidden)


@router.get("/folders/{folder_id}")
def folder_details(folder_id: str):
    token = get_token()
    return get_folder_details(token, folder_id)


@router.post("/folders")
def create_new_folder(display_name: str):
    token = get_token()
    return create_folder(token, display_name)


@router.post("/folders/{parent_folder_id}/child")
def create_new_child_folder(parent_folder_id: str, display_name: str):
    token = get_token()
    return create_child_folder(token, parent_folder_id, display_name)


@router.patch("/folders/{folder_id}")
def update_folder(folder_id: str, display_name: str):
    token = get_token()
    return modify_folder(token, folder_id, display_name)


@router.delete("/folders/{folder_id}")
def remove_folder(folder_id: str):
    token = get_token()
    return delete_folder(token, folder_id)


#Drafts

@router.get("/drafts")
def list_drafts(max_results: int = 10):
    token = get_token()
    return list_draft_email_messages(token, max_results=max_results)


@router.get("/drafts/{draft_id}")
def draft_details(draft_id: str):
    token = get_token()
    return get_draft_email_details(token, draft_id)


@router.post("/drafts")
def create_draft(to: str, subject: str, body: str, body_type: str = "Text"):
    token = get_token()
    return create_draft_email(token, to, subject, body, body_type=body_type)


@router.patch("/drafts/{draft_id}")
def update_draft(draft_id: str, request: UpdateDraftRequest):
    token = get_token()
    updates = {}
    if request.subject is not None:
        updates['subject'] = request.subject
    if request.body is not None:
        updates['body'] = request.body
    if request.body_type is not None:
        updates['body_type'] = request.body_type
    if request.to is not None:
        updates['to'] = request.to
    if request.cc is not None:
        updates['cc'] = request.cc
    if request.bcc is not None:
        updates['bcc'] = request.bcc
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    return update_draft_email(token, draft_id, **updates)


@router.post("/drafts/{draft_id}/send")
def send_draft(draft_id: str):
    token = get_token()
    return send_draft_email(token, draft_id)


@router.delete("/drafts/{draft_id}")
def remove_draft(draft_id: str):
    token = get_token()
    return delete_draft_email(token, draft_id)

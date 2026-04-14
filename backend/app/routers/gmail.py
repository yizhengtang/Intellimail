import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from Gmail.gmail_api import (
    initialize_gmail_service,
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
    get_attachment_list,
    get_attachment_data,
    create_label,
    list_labels,
    get_label_details,
    modify_labels,
    delete_label,
    modify_email_labels,
    trash_email,
    trash_email_in_batch,
    untrash_email,
    untrash_email_in_batch,
    delete_email,
    empty_trash,
    create_draft_email,
    list_draft_email_messages,
    get_draft_email_details,
    send_draft_email,
    delete_draft_email,
)

router = APIRouter()

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Gmail', 'downloads')


def get_service():
    try:
        return initialize_gmail_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Gmail service: {e}")


# Request body models

class BatchMessageIdsRequest(BaseModel):
    message_ids: List[str]

class ModifyEmailLabelsRequest(BaseModel):
    add_labels: Optional[List[str]] = None
    remove_labels: Optional[List[str]] = None

class UpdateLabelRequest(BaseModel):
    name: Optional[str] = None
    label_list_visibility: Optional[str] = None
    message_list_visibility: Optional[str] = None


# Emails

@router.get("/emails")
def list_emails(folder: str = "INBOX", max_results: int = 10):
    service = get_service()
    return get_email_messages(service, folder_name=folder, max_results=max_results)


@router.get("/emails/{message_id}/conversations")
def email_conversations(message_id: str):
    service = get_service()
    return get_email_conversations(service, message_id)


@router.get("/emails/{message_id}")
def email_details(message_id: str):
    service = get_service()
    return get_email_message_details(service, message_id)


# Search

@router.get("/search")
def search(query: str, max_results: int = 5):
    service = get_service()
    return search_emails(service, query, max_results=max_results)


@router.get("/search/conversations")
def search_conversations(query: str, max_results: int = 5):
    service = get_service()
    return search_email_conversations(service, query, max_results=max_results)


# Send and reply

@router.post("/send")
def send_email(to: str, subject: str, body: str, body_type: str = "plain"):
    service = get_service()
    return send_email_with_attachment(service, to, subject, body, body_type=body_type)


@router.post("/emails/{message_id}/reply")
def reply(message_id: str, body: str, body_type: str = "plain"):
    service = get_service()
    return reply_email(service, message_id, body, body_type=body_type)


@router.post("/emails/{message_id}/reply-all")
def reply_all(message_id: str, body: str, body_type: str = "plain"):
    service = get_service()
    return reply_all_email(service, message_id, body, body_type=body_type)


# Attachments

@router.get("/emails/{message_id}/attachments/download")
def download_email_attachments(message_id: str):
    service = get_service()
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    download_attachments(service, 'me', message_id, DOWNLOADS_DIR)
    return {"message": "Attachments downloaded", "download_dir": DOWNLOADS_DIR}


@router.get("/emails/{message_id}/attachments/download-all")
def download_all_thread_attachments(message_id: str):
    service = get_service()
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    download_attachments_all(service, 'me', message_id, DOWNLOADS_DIR)
    return {"message": "All thread attachments downloaded", "download_dir": DOWNLOADS_DIR}


#Returns the attachment metadata list for an email — id, filename, content_type, size.
#The frontend uses this to render attachment chips and inline images.
@router.get("/emails/{message_id}/attachments")
def list_attachments(message_id: str):
    service = get_service()
    return get_attachment_list(service, message_id)


#Streams a single attachment directly to the browser.
#Images get Content-Disposition: inline so the browser renders them.
#Everything else gets Content-Disposition: attachment so the browser downloads the file.
@router.get("/emails/{message_id}/attachments/{attachment_id}")
def stream_attachment(message_id: str, attachment_id: str):
    service = get_service()
    data, filename, content_type = get_attachment_data(service, message_id, attachment_id)
    if content_type.startswith('image/'):
        disposition = 'inline'
    else:
        disposition = f'attachment; filename="{filename}"'
    return StreamingResponse(
        iter([data]),
        media_type=content_type,
        headers={'Content-Disposition': disposition}
    )


# Trash

@router.post("/emails/trash/batch")
def trash_batch(request: BatchMessageIdsRequest):
    service = get_service()
    return trash_email_in_batch(service, 'me', request.message_ids)


@router.post("/emails/untrash/batch")
def untrash_batch(request: BatchMessageIdsRequest):
    service = get_service()
    return untrash_email_in_batch(service, 'me', request.message_ids)


@router.post("/emails/{message_id}/trash")
def trash(message_id: str):
    service = get_service()
    return trash_email(service, 'me', message_id)


@router.post("/emails/{message_id}/untrash")
def untrash(message_id: str):
    service = get_service()
    return untrash_email(service, 'me', message_id)


@router.delete("/emails/{message_id}")
def delete(message_id: str):
    service = get_service()
    return delete_email(service, 'me', message_id)


@router.post("/trash/empty")
def empty_trash_endpoint():
    service = get_service()
    total = empty_trash(service)
    return {"total_deleted": total}


# Labels

@router.get("/labels")
def get_labels():
    service = get_service()
    return list_labels(service)


@router.get("/labels/{label_id}")
def label_details(label_id: str):
    service = get_service()
    return get_label_details(service, label_id)


@router.post("/labels")
def create_new_label(name: str):
    service = get_service()
    return create_label(service, name)


@router.patch("/labels/{label_id}")
def update_label(label_id: str, request: UpdateLabelRequest):
    service = get_service()
    updates = {}
    if request.name is not None:
        updates['name'] = request.name
    if request.label_list_visibility is not None:
        updates['labelListVisibility'] = request.label_list_visibility
    if request.message_list_visibility is not None:
        updates['messageListVisibility'] = request.message_list_visibility
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    return modify_labels(service, label_id, **updates)


@router.delete("/labels/{label_id}")
def remove_label(label_id: str):
    service = get_service()
    return delete_label(service, label_id)


@router.post("/emails/{message_id}/labels")
def update_email_labels(message_id: str, request: ModifyEmailLabelsRequest):
    service = get_service()
    return modify_email_labels(service, 'me', message_id,
                               add_labels=request.add_labels,
                               remove_labels=request.remove_labels)


# Drafts

@router.get("/drafts")
def list_drafts(max_results: int = 10):
    service = get_service()
    return list_draft_email_messages(service, max_results=max_results)


@router.get("/drafts/{draft_id}")
def draft_details(draft_id: str):
    service = get_service()
    return get_draft_email_details(service, draft_id)


@router.post("/drafts")
def create_draft(to: str, subject: str, body: str, body_type: str = "plain"):
    service = get_service()
    return create_draft_email(service, to, subject, body, body_type=body_type)


@router.post("/drafts/{draft_id}/send")
def send_draft(draft_id: str):
    service = get_service()
    return send_draft_email(service, draft_id)


@router.delete("/drafts/{draft_id}")
def remove_draft(draft_id: str):
    service = get_service()
    return delete_draft_email(service, draft_id)

from fastapi import APIRouter, HTTPException, Query
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
    download_attachments_all,
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


def get_service():
    try:
        return initialize_gmail_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Gmail service: {e}")


# ── Emails ──

@router.get("/emails")
def list_emails(folder: str = "INBOX", max_results: int = 10):
    service = get_service()
    return get_email_messages(service, folder_name=folder, max_results=max_results)


@router.get("/emails/{message_id}")
def email_details(message_id: str):
    service = get_service()
    return get_email_message_details(service, message_id)


@router.get("/emails/{message_id}/conversations")
def email_conversations(message_id: str):
    service = get_service()
    return get_email_conversations(service, message_id)


# ── Search ──

@router.get("/search")
def search(query: str, max_results: int = 5):
    service = get_service()
    return search_emails(service, query, max_results=max_results)


@router.get("/search/conversations")
def search_conversations(query: str, max_results: int = 5):
    service = get_service()
    return search_email_conversations(service, query, max_results=max_results)


# ── Send / Reply ──

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


# ── Trash ──

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


# ── Labels ──

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


@router.delete("/labels/{label_id}")
def remove_label(label_id: str):
    service = get_service()
    return delete_label(service, label_id)


# ── Drafts ──

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

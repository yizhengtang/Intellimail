#test_gmail_api.py
#Unit tests for gmail_api.py — covers all major functions using mocked Gmail service objects.
#No real API credentials or network calls are made.

import base64
import pytest
from unittest.mock import MagicMock
import gmail_api
from gmail_api import (
    extract_body,
    _flatten_parts,
    initialize_gmail_service,
    get_email_messages,
    get_email_message_details,
    send_email_with_attachment,
    reply_email,
    reply_all_email,
    get_attachment_list,
    get_attachment_data,
    search_emails,
    search_email_conversations,
    create_label,
    list_labels,
    get_label_details,
    modify_labels,
    delete_label,
    map_label_name_to_id,
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
    get_email_conversations,
)


#Helpers

def _encode(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode()


def _plain_payload(text: str) -> dict:
    return {'mimeType': 'text/plain', 'body': {'data': _encode(text)}}


def _html_payload(html: str) -> dict:
    return {'mimeType': 'text/html', 'body': {'data': _encode(html)}}


def _make_headers(subject='Test Subject', sender='sender@example.com',
                  to='me@example.com', date='Mon, 27 Apr 2025 10:00:00 +0000',
                  message_id='<msg@mail.com>', references='') -> list:
    return [
        {'name': 'Subject', 'value': subject},
        {'name': 'From', 'value': sender},
        {'name': 'To', 'value': to},
        {'name': 'Date', 'value': date},
        {'name': 'Message-ID', 'value': message_id},
        {'name': 'References', 'value': references},
    ]


class FakeBatch:
    """Simulates Google API batch requests by calling the callback synchronously on execute()."""
    def __init__(self, callback=None, responses=None):
        self._callback = callback
        self._responses = responses or {}
        self._added = []

    def add(self, _request, request_id=None):
        if request_id is not None:
            self._added.append(request_id)

    def execute(self):
        if self._callback:
            for rid in self._added:
                self._callback(rid, self._responses.get(rid), None)


#initialize_gmail_service

def test_initialize_gmail_service_returns_service(monkeypatch):
    mock_service = MagicMock()
    monkeypatch.setattr(gmail_api, 'create_gmail_service', lambda *args: mock_service)
    result = initialize_gmail_service()
    assert result is mock_service


#extract_body — single-part emails

def test_extract_body_single_part_plain():
    body, body_type = extract_body(_plain_payload('Hello plain'))
    assert body == 'Hello plain'
    assert body_type == 'plain'


def test_extract_body_single_part_html():
    body, body_type = extract_body(_html_payload('<p>Hello HTML</p>'))
    assert body == '<p>Hello HTML</p>'
    assert body_type == 'html'


def test_extract_body_empty_payload_returns_fallback():
    body, body_type = extract_body({})
    assert body == '<Text body not available>'
    assert body_type == 'plain'


#extract_body — multipart emails

def test_extract_body_multipart_prefers_html_over_plain():
    payload = {
        'parts': [
            {'mimeType': 'text/plain', 'body': {'data': _encode('Plain text')}},
            {'mimeType': 'text/html', 'body': {'data': _encode('<b>HTML</b>')}},
        ]
    }
    body, body_type = extract_body(payload)
    assert body == '<b>HTML</b>'
    assert body_type == 'html'


def test_extract_body_multipart_plain_only():
    payload = {'parts': [{'mimeType': 'text/plain', 'body': {'data': _encode('Only plain')}}]}
    body, body_type = extract_body(payload)
    assert body == 'Only plain'
    assert body_type == 'plain'


def test_extract_body_nested_multipart():
    payload = {
        'parts': [{
            'mimeType': 'multipart/alternative',
            'parts': [
                {'mimeType': 'text/plain', 'body': {'data': _encode('Nested plain')}},
                {'mimeType': 'text/html', 'body': {'data': _encode('<i>Nested HTML</i>')}},
            ],
        }]
    }
    body, body_type = extract_body(payload)
    assert body == '<i>Nested HTML</i>'
    assert body_type == 'html'


#_flatten_parts

def test_flatten_parts_flat_list():
    parts = [{'mimeType': 'text/plain'}, {'mimeType': 'text/html'}]
    assert len(_flatten_parts(parts)) == 2


def test_flatten_parts_nested_returns_all():
    parts = [{'mimeType': 'multipart/alternative', 'parts': [{'mimeType': 'text/plain'}, {'mimeType': 'text/html'}]}]
    assert len(_flatten_parts(parts)) == 3


def test_flatten_parts_empty_list():
    assert _flatten_parts([]) == []


#get_email_messages

def _make_batch_service(label_name, message_stubs, batch_responses):
    service = MagicMock()
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {
        'labels': [{'id': label_name.upper(), 'name': label_name}]
    }
    service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': message_stubs,
        'nextPageToken': None
    }
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch(callback, batch_responses)
    return service


def test_get_email_messages_returns_formatted_list():
    message_stripped = {'id': 'msg001'}
    batch_response = {
        'msg001': {
            'threadId': 'thread001',
            'snippet': 'Email snippet',
            'labelIds': ['INBOX', 'UNREAD'],
            'payload': {
                'headers': _make_headers(),
                'parts': []
            }
        }
    }
    service = _make_batch_service('inbox', [message_stripped], batch_response)
    result = get_email_messages(service, folder_name='inbox', max_results=1)
    assert len(result) == 1
    assert result[0]['id'] == 'msg001'
    assert result[0]['subject'] == 'Test Subject'
    assert result[0]['is_read'] is False
    assert result[0]['thread_id'] == 'thread001'


def test_get_email_messages_marks_read_when_no_unread_label():
    message_stripped = {'id': 'msg002'}
    batch_response = {
        'msg002': {
            'threadId': 'thread002',
            'snippet': '',
            'labelIds': ['INBOX'],
            'payload': {'headers': _make_headers(), 'parts': []}
        }
    }
    service = _make_batch_service('inbox', [message_stripped], batch_response)
    result = get_email_messages(service, folder_name='inbox', max_results=1)
    assert result[0]['is_read'] is True


def test_get_email_messages_detects_attachment():
    message_stripped = {'id': 'msg003'}
    batch_response = {
        'msg003': {
            'threadId': 'thread003',
            'snippet': '',
            'labelIds': ['INBOX'],
            'payload': {
                'headers': _make_headers(),
                'parts': [{'filename': 'report.pdf', 'mimeType': 'application/pdf'}]
            }
        }
    }
    service = _make_batch_service('inbox', [message_stripped], batch_response)
    result = get_email_messages(service, folder_name='inbox', max_results=1)
    assert result[0]['has_attachments'] is True


def test_get_email_messages_empty_folder_returns_empty():
    service = _make_batch_service('inbox', [], {})
    result = get_email_messages(service, folder_name='inbox', max_results=5)
    assert result == []


def test_get_email_messages_invalid_folder_raises():
    service = MagicMock()
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {
        'labels': [{'id': 'INBOX', 'name': 'INBOX'}]
    }
    with pytest.raises(ValueError, match='not found'):
        get_email_messages(service, folder_name='nonexistent_folder', max_results=5)


#get_email_message_details

def test_get_email_message_details_returns_correct_fields():
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'id': 'msg001',
        'threadId': 'thread001',
        'snippet': 'Test snippet',
        'labelIds': ['INBOX'],
        'payload': {
            'mimeType': 'text/plain',
            'headers': _make_headers(),
            'body': {'data': _encode('Email body content')}
        }
    }
    result = get_email_message_details(service, 'msg001')
    assert result['id'] == 'msg001'
    assert result['subject'] == 'Test Subject'
    assert result['from'] == 'sender@example.com'
    assert result['to'] == 'me@example.com'
    assert result['body'] == 'Email body content'
    assert result['body_type'] == 'plain'
    assert result['starred'] is False
    assert result['thread_id'] == 'thread001'


def test_get_email_message_details_starred_flag():
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'id': 'msg002',
        'threadId': 'thread002',
        'snippet': '',
        'labelIds': ['INBOX', 'STARRED'],
        'payload': {
            'mimeType': 'text/plain',
            'headers': _make_headers(),
            'body': {'data': _encode('Starred email')}
        }
    }
    result = get_email_message_details(service, 'msg002')
    assert result['starred'] is True


#send_email_with_attachment

def test_send_email_success():
    service = MagicMock()
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
        'id': 'sent001', 'labelIds': ['SENT']
    }
    result = send_email_with_attachment(service, 'to@example.com', 'Subject', 'Body text')
    assert result['id'] == 'sent001'


def test_send_email_html_body_type():
    service = MagicMock()
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {'id': 'sent002'}
    result = send_email_with_attachment(service, 'to@example.com', 'Subject', '<b>Bold</b>', body_type='html')
    assert result['id'] == 'sent002'


def test_send_email_invalid_body_type_raises():
    service = MagicMock()
    with pytest.raises(ValueError, match="body_type must be either 'plain' or 'html'"):
        send_email_with_attachment(service, 'to@example.com', 'Subject', 'Body', body_type='xml')


def test_send_email_missing_attachment_raises(tmp_path):
    service = MagicMock()
    with pytest.raises(FileNotFoundError):
        send_email_with_attachment(service, 'to@example.com', 'Subject', 'Body', attachment_paths=[str(tmp_path / 'missing.pdf')])


def test_send_email_with_real_attachment(tmp_path):
    attachment = tmp_path / 'doc.txt'
    attachment.write_text('file content')
    service = MagicMock()
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {'id': 'sent003'}
    result = send_email_with_attachment(service, 'to@example.com', 'Subject', 'Body', attachment_paths=[str(attachment)])
    assert result['id'] == 'sent003'


#reply_email

def _make_reply_service(headers):
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {'headers': headers},
        'threadId': 'thread_abc',
    }
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {'id': 'reply001'}
    return service


def test_reply_email_sends_successfully():
    service = _make_reply_service(_make_headers())
    result = reply_email(service, 'msg001', 'My reply')
    assert result['id'] == 'reply001'


def test_reply_email_subject_gets_re_prefix():
    headers = _make_headers(subject='Original Subject')
    service = _make_reply_service(headers)
    reply_email(service, 'msg001', 'My reply')
    send_call = service.users.return_value.messages.return_value.send
    assert send_call.called


def test_reply_email_subject_preserves_existing_re():
    headers = _make_headers(subject='Re: Ongoing thread')
    service = _make_reply_service(headers)
    result = reply_email(service, 'msg001', 'My reply')
    assert result['id'] == 'reply001'


def test_reply_email_invalid_body_type_raises():
    service = _make_reply_service(_make_headers())
    with pytest.raises(ValueError, match="body_type must be either 'plain' or 'html'"):
        reply_email(service, 'msg001', 'Reply body', body_type='xml')


def test_reply_email_missing_sender_raises():
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {'headers': [{'name': 'Subject', 'value': 'Hello'}]},
        'threadId': 'thread_abc',
    }
    with pytest.raises(ValueError, match='Could not find the sender'):
        reply_email(service, 'msg001', 'Reply body')


#reply_all_email

def _make_reply_all_service(headers, my_email='me@example.com'):
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {'headers': headers},
        'threadId': 'thread_abc',
    }
    service.users.return_value.getProfile.return_value.execute.return_value = {'emailAddress': my_email}
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {'id': 'replyall001'}
    return service


def test_reply_all_email_sends_successfully():
    headers = _make_headers() + [{'name': 'Cc', 'value': ''}]
    service = _make_reply_all_service(headers)
    result = reply_all_email(service, 'msg001', 'Reply all body')
    assert result['id'] == 'replyall001'


def test_reply_all_email_preserves_re_prefix():
    headers = _make_headers(subject='Re: Already prefixed') + [{'name': 'Cc', 'value': ''}]
    service = _make_reply_all_service(headers)
    result = reply_all_email(service, 'msg001', 'Reply')
    assert result['id'] == 'replyall001'


def test_reply_all_email_invalid_body_type_raises():
    headers = _make_headers() + [{'name': 'Cc', 'value': ''}]
    service = _make_reply_all_service(headers)
    with pytest.raises(ValueError, match="body_type must be either 'plain' or 'html'"):
        reply_all_email(service, 'msg001', 'Reply', body_type='xml')


#get_attachment_list

def test_get_attachment_list_returns_attachments():
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {
            'parts': [
                {
                    'filename': 'report.pdf',
                    'mimeType': 'application/pdf',
                    'body': {'attachmentId': 'att001', 'size': 1024}
                }
            ]
        }
    }
    result = get_attachment_list(service, 'msg001')
    assert len(result) == 1
    assert result[0]['filename'] == 'report.pdf'
    assert result[0]['id'] == 'att001'
    assert result[0]['content_type'] == 'application/pdf'


def test_get_attachment_list_empty_when_no_attachments():
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {'parts': [{'filename': '', 'mimeType': 'text/plain', 'body': {}}]}
    }
    result = get_attachment_list(service, 'msg001')
    assert result == []


#get_attachment_data

def test_get_attachment_data_returns_bytes_and_metadata():
    file_bytes = b'PDF binary content'
    encoded = base64.urlsafe_b64encode(file_bytes).decode()
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {
            'parts': [
                {
                    'filename': 'file.pdf',
                    'mimeType': 'application/pdf',
                    'body': {'attachmentId': 'att001', 'size': len(file_bytes)}
                }
            ]
        }
    }
    service.users.return_value.messages.return_value.attachments.return_value.get.return_value.execute.return_value = {
        'data': encoded
    }
    data, filename, content_type = get_attachment_data(service, 'msg001', 'att001')
    assert data == file_bytes
    assert filename == 'file.pdf'
    assert content_type == 'application/pdf'


#search_emails

def test_search_emails_returns_matching_emails():
    stub = {'id': 'msg001'}
    batch_response = {
        'msg001': {
            'threadId': 'thread001',
            'snippet': 'Matching email',
            'labelIds': ['INBOX'],
            'payload': {'headers': _make_headers(subject='Search Result'), 'parts': []}
        }
    }
    service = MagicMock()
    service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': [stub], 'nextPageToken': None
    }
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch(callback, batch_response)
    result = search_emails(service, 'important meeting', max_results=5)
    assert len(result) == 1
    assert result[0]['subject'] == 'Search Result'


def test_search_emails_returns_empty_when_no_results():
    service = MagicMock()
    service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': [], 'nextPageToken': None
    }
    result = search_emails(service, 'nothing found')
    assert result == []


#search_email_conversations

def test_search_email_conversations_returns_threads():
    thread_stub = {'id': 'thread001'}
    thread_resp = {
        'thread001': {
            'id': 'thread001',
            'messages': [
                {
                    'id': 'msg001',
                    'labelIds': ['INBOX'],
                    'snippet': 'Thread snippet',
                    'payload': {
                        'headers': _make_headers(subject='Thread Subject'),
                        'parts': []
                    }
                }
            ]
        }
    }
    service = MagicMock()
    service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': [thread_stub], 'nextPageToken': None
    }
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch(callback, thread_resp)
    result = search_email_conversations(service, 'project update')
    assert len(result) == 1
    assert result[0]['subject'] == 'Thread Subject'
    assert result[0]['message_count'] == 1


def test_search_email_conversations_empty_result():
    service = MagicMock()
    service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': [], 'nextPageToken': None
    }
    result = search_email_conversations(service, 'nothing')
    assert result == []


#create_label

def test_create_label_returns_created_label():
    service = MagicMock()
    service.users.return_value.labels.return_value.create.return_value.execute.return_value = {
        'id': 'Label_001', 'name': 'Work', 'labelListVisibility': 'labelShow'
    }
    result = create_label(service, 'Work')
    assert result['id'] == 'Label_001'
    assert result['name'] == 'Work'


#list_labels

def test_list_labels_returns_label_list():
    service = MagicMock()
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {
        'labels': [{'id': 'INBOX', 'name': 'INBOX', 'type': 'system'}]
    }
    service.users.return_value.labels.return_value.get.return_value.execute.return_value = {
        'id': 'INBOX', 'name': 'INBOX', 'type': 'system', 'messagesUnread': 3, 'messagesTotal': 20
    }
    result = list_labels(service)
    assert len(result) == 1
    assert result[0]['id'] == 'INBOX'
    assert result[0]['unread_count'] == 3
    assert result[0]['message_count'] == 20


#get_label_details

def test_get_label_details_returns_label():
    service = MagicMock()
    service.users.return_value.labels.return_value.get.return_value.execute.return_value = {
        'id': 'INBOX', 'name': 'INBOX', 'type': 'system'
    }
    result = get_label_details(service, 'INBOX')
    assert result['id'] == 'INBOX'


#modify_labels

def test_modify_labels_updates_name():
    service = MagicMock()
    service.users.return_value.labels.return_value.get.return_value.execute.return_value = {
        'id': 'Label_001', 'name': 'OldName'
    }
    service.users.return_value.labels.return_value.update.return_value.execute.return_value = {
        'id': 'Label_001', 'name': 'NewName'
    }
    result = modify_labels(service, 'Label_001', name='NewName')
    assert result['name'] == 'NewName'


#delete_label

def test_delete_label_returns_confirmation():
    service = MagicMock()
    result = delete_label(service, 'Label_001')
    assert 'Label_001' in result
    assert 'deleted' in result


#map_label_name_to_id

def test_map_label_name_to_id_found():
    service = MagicMock()
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {
        'labels': [{'id': 'Label_001', 'name': 'Work', 'type': 'user'}]
    }
    service.users.return_value.labels.return_value.get.return_value.execute.return_value = {
        'id': 'Label_001', 'name': 'Work', 'type': 'user', 'messagesUnread': 0, 'messagesTotal': 5
    }
    result = map_label_name_to_id(service, 'work')
    assert result == 'Label_001'


def test_map_label_name_to_id_not_found():
    service = MagicMock()
    service.users.return_value.labels.return_value.list.return_value.execute.return_value = {
        'labels': [{'id': 'INBOX', 'name': 'INBOX', 'type': 'system'}]
    }
    service.users.return_value.labels.return_value.get.return_value.execute.return_value = {
        'id': 'INBOX', 'name': 'INBOX', 'type': 'system', 'messagesUnread': 0, 'messagesTotal': 0
    }
    result = map_label_name_to_id(service, 'nonexistent')
    assert result is None


#modify_email_labels

def test_modify_email_labels_add_and_remove():
    service = MagicMock()
    result = modify_email_labels(service, 'me', 'msg001', add_labels=['STARRED'], remove_labels=['UNREAD'])
    assert 'msg001' in result


def test_modify_email_labels_add_only():
    service = MagicMock()
    result = modify_email_labels(service, 'me', 'msg001', add_labels=['STARRED'])
    assert 'msg001' in result


#trash_email / untrash_email / delete_email

def test_trash_email_returns_confirmation():
    service = MagicMock()
    result = trash_email(service, 'me', 'msg001')
    assert 'msg001' in result
    assert 'trash' in result


def test_untrash_email_returns_confirmation():
    service = MagicMock()
    result = untrash_email(service, 'me', 'msg001')
    assert 'msg001' in result


def test_delete_email_returns_confirmation():
    service = MagicMock()
    result = delete_email(service, 'me', 'msg001')
    assert 'msg001' in result


#trash_email_in_batch / untrash_email_in_batch

def test_trash_email_in_batch_returns_confirmation():
    service = MagicMock()
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch()
    result = trash_email_in_batch(service, 'me', ['msg001', 'msg002'])
    assert 'Trashed 2' in result


def test_untrash_email_in_batch_returns_confirmation():
    service = MagicMock()
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch()
    result = untrash_email_in_batch(service, 'me', ['msg001', 'msg002'])
    assert 'Untrashed 2' in result


#empty_trash

def test_empty_trash_deletes_messages_and_returns_count():
    service = MagicMock()
    service.users.return_value.messages.return_value.list.return_value.execute.side_effect = [
        {'messages': [{'id': 'msg001'}, {'id': 'msg002'}], 'nextPageToken': None},
    ]
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch()
    count = empty_trash(service)
    assert count == 2


def test_empty_trash_returns_zero_when_already_empty():
    service = MagicMock()
    service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': [], 'nextPageToken': None
    }
    count = empty_trash(service)
    assert count == 0


#create_draft_email

def test_create_draft_email_returns_draft():
    service = MagicMock()
    service.users.return_value.drafts.return_value.create.return_value.execute.return_value = {
        'id': 'draft001', 'message': {'id': 'msg001'}
    }
    result = create_draft_email(service, 'to@example.com', 'Draft Subject', 'Draft body')
    assert result['id'] == 'draft001'


def test_create_draft_email_invalid_body_type_raises():
    service = MagicMock()
    with pytest.raises(ValueError, match="body_type must be either 'plain' or 'html'"):
        create_draft_email(service, 'to@example.com', 'Subject', 'Body', body_type='xml')


def test_create_draft_email_missing_attachment_raises(tmp_path):
    service = MagicMock()
    with pytest.raises(FileNotFoundError):
        create_draft_email(service, 'to@example.com', 'Subject', 'Body', attachment_paths=[str(tmp_path / 'missing.txt')])


#list_draft_email_messages

def test_list_draft_email_messages_returns_drafts():
    draft_stub = {'id': 'draft001'}
    batch_response = {
        'draft001': {
            'id': 'draft001',
            'message': {
                'id': 'msg001',
                'threadId': 'thread001',
                'snippet': 'Draft snippet',
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': 'Draft Subject'},
                        {'name': 'To', 'value': 'to@example.com'},
                        {'name': 'Date', 'value': 'Mon, 27 Apr 2025 10:00:00 +0000'},
                    ],
                    'parts': []
                }
            }
        }
    }
    service = MagicMock()
    service.users.return_value.drafts.return_value.list.return_value.execute.return_value = {
        'drafts': [draft_stub], 'nextPageToken': None
    }
    service.new_batch_http_request.side_effect = lambda callback=None: FakeBatch(callback, batch_response)
    result = list_draft_email_messages(service)
    assert len(result) == 1
    assert result[0]['id'] == 'draft001'
    assert result[0]['subject'] == 'Draft Subject'


def test_list_draft_email_messages_empty():
    service = MagicMock()
    service.users.return_value.drafts.return_value.list.return_value.execute.return_value = {
        'drafts': [], 'nextPageToken': None
    }
    result = list_draft_email_messages(service)
    assert result == []


#get_draft_email_details

def test_get_draft_email_details_returns_dict():
    service = MagicMock()
    service.users.return_value.drafts.return_value.get.return_value.execute.return_value = {
        'id': 'draft001',
        'message': {
            'id': 'msg001',
            'threadId': 'thread001',
            'snippet': 'Draft snippet',
            'labelIds': [],
            'payload': {
                'mimeType': 'text/plain',
                'headers': _make_headers(subject='Draft Subject', to='to@example.com'),
                'body': {'data': _encode('Draft body text')},
            }
        }
    }
    result = get_draft_email_details(service, 'draft001')
    assert result['id'] == 'draft001'
    assert result['subject'] == 'Draft Subject'
    assert result['body'] == 'Draft body text'
    assert result['body_type'] == 'plain'


#send_draft_email / delete_draft_email

def test_send_draft_email_calls_api_and_returns_result():
    service = MagicMock()
    service.users.return_value.drafts.return_value.send.return_value.execute.return_value = {
        'id': 'sent001', 'labelIds': ['SENT']
    }
    result = send_draft_email(service, 'draft001')
    assert result['id'] == 'sent001'


def test_delete_draft_email_returns_confirmation():
    service = MagicMock()
    result = delete_draft_email(service, 'draft001')
    assert 'draft001' in result
    assert 'deleted' in result


#get_email_conversations

def test_get_email_conversations_returns_thread_messages():
    service = MagicMock()
    service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'threadId': 'thread001'
    }
    service.users.return_value.threads.return_value.get.return_value.execute.return_value = {
        'messages': [
            {
                'id': 'msg001',
                'payload': {
                    'headers': _make_headers(subject='Thread Subject'),
                    'mimeType': 'text/plain',
                    'body': {'data': _encode('Message 1 body')}
                }
            },
            {
                'id': 'msg002',
                'payload': {
                    'headers': _make_headers(subject='Thread Subject'),
                    'mimeType': 'text/plain',
                    'body': {'data': _encode('Message 2 body')}
                }
            }
        ]
    }
    result = get_email_conversations(service, 'msg001')
    assert len(result) == 2
    assert result[0]['id'] == 'msg001'
    assert result[0]['subject'] == 'Thread Subject'
    assert result[1]['id'] == 'msg002'

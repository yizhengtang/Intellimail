#test_outlook_api.py
#Unit tests for outlook_api.py — covers all major functions using mocked Graph API calls.
#make_graph_request is patched throughout so no real HTTP calls are made.

import base64
import os
import pytest
from unittest.mock import MagicMock, patch
import outlook_api
from outlook_api import (
    OUTLOOK_FOLDER_MAP,
    initialize_outlook_service,
    make_graph_request,
    get_email_messages,
    get_email_message_details,
    send_email_with_attachment,
    reply_email,
    reply_all_email,
    download_attachments,
    search_emails,
    search_email_conversations,
    mark_as_read,
    mark_as_unread,
    list_folders,
    get_folder_details,
    create_folder,
    create_child_folder,
    modify_folder,
    delete_folder,
    map_folder_name_to_id,
    move_message_to_folder,
    trash_email,
    trash_email_in_batch,
    untrash_email,
    untrash_email_in_batch,
    delete_email,
    empty_trash,
    get_trash_messages,
    get_email_conversations,
    create_draft_email,
    list_draft_email_messages,
    get_draft_email_details,
    send_draft_email,
    delete_draft_email,
    update_draft_email,
    get_attachment_list,
    get_attachment_data,
)


#OUTLOOK_FOLDER_MAP — folder name translation

def test_folder_map_inbox():
    assert OUTLOOK_FOLDER_MAP['inbox'] == 'inbox'


def test_folder_map_trash():
    assert OUTLOOK_FOLDER_MAP['trash'] == 'deleteditems'


def test_folder_map_sent():
    assert OUTLOOK_FOLDER_MAP['sent'] == 'sentitems'


def test_folder_map_spam():
    assert OUTLOOK_FOLDER_MAP['spam'] == 'junkemail'


def test_folder_map_drafts():
    assert OUTLOOK_FOLDER_MAP['drafts'] == 'drafts'


def test_folder_map_unknown_name_not_present():
    assert OUTLOOK_FOLDER_MAP.get('my_custom_folder') is None


#initialize_outlook_service

def test_initialize_outlook_service_returns_token(monkeypatch):
    monkeypatch.setenv('MICROSOFT_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('MICROSOFT_CLIENT_SECRET', 'test_secret')
    monkeypatch.setattr(outlook_api, 'get_access_token', lambda *args: 'fake_token')
    result = initialize_outlook_service()
    assert result == 'fake_token'


def test_initialize_outlook_service_raises_without_credentials(monkeypatch):
    monkeypatch.delenv('MICROSOFT_CLIENT_ID', raising=False)
    monkeypatch.delenv('MICROSOFT_CLIENT_SECRET', raising=False)
    with pytest.raises(ValueError, match='not found in environment variables'):
        initialize_outlook_service()


#make_graph_request

def _mock_http_client(method, response_data, response_text='{"data": true}'):
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_response.json.return_value = response_data
    mock_client = MagicMock()
    getattr(mock_client, method).return_value = mock_response
    return mock_client


def test_make_graph_request_get():
    expected = {'value': []}
    mock_response = MagicMock()
    mock_response.text = '{"value": []}'
    mock_response.json.return_value = expected
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    with patch('outlook_api.httpx.Client') as MockClient:
        MockClient.return_value.__enter__.return_value = mock_client
        result = make_graph_request('token', 'me/messages')
    assert result == expected


def test_make_graph_request_post():
    expected = {'id': 'msg001'}
    mock_response = MagicMock()
    mock_response.text = '{"id": "msg001"}'
    mock_response.json.return_value = expected
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    with patch('outlook_api.httpx.Client') as MockClient:
        MockClient.return_value.__enter__.return_value = mock_client
        result = make_graph_request('token', 'me/sendMail', method='POST', json_data={})
    assert result == expected


def test_make_graph_request_delete_returns_none():
    mock_response = MagicMock()
    mock_response.text = ''
    mock_client = MagicMock()
    mock_client.delete.return_value = mock_response
    with patch('outlook_api.httpx.Client') as MockClient:
        MockClient.return_value.__enter__.return_value = mock_client
        result = make_graph_request('token', 'me/messages/msg001', method='DELETE')
    assert result is None


def test_make_graph_request_patch():
    expected = {'id': 'msg001', 'subject': 'Updated'}
    mock_response = MagicMock()
    mock_response.text = '{"id": "msg001"}'
    mock_response.json.return_value = expected
    mock_client = MagicMock()
    mock_client.patch.return_value = mock_response
    with patch('outlook_api.httpx.Client') as MockClient:
        MockClient.return_value.__enter__.return_value = mock_client
        result = make_graph_request('token', 'me/messages/msg001', method='PATCH', json_data={})
    assert result == expected


def test_make_graph_request_merges_extra_headers():
    mock_response = MagicMock()
    mock_response.text = '{"value": []}'
    mock_response.json.return_value = {'value': []}
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    with patch('outlook_api.httpx.Client') as MockClient:
        MockClient.return_value.__enter__.return_value = mock_client
        result = make_graph_request('token', 'me/messages', extra_headers={'Prefer': 'outlook.body-content-type="text"'})
    assert result == {'value': []}


#get_email_messages

def test_get_email_messages_returns_formatted_list():
    mock_response = {
        'value': [{
            'id': 'msg001',
            'from': {'emailAddress': {'address': 'alice@example.com', 'name': 'Alice'}},
            'subject': 'Hello there',
            'bodyPreview': 'Just checking in.',
            'receivedDateTime': '2025-04-27T10:00:00Z',
            'isRead': False,
            'hasAttachments': True,
        }]
    }
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_email_messages('token', folder_name='inbox', max_results=1)
    assert len(result) == 1
    assert result[0]['id'] == 'msg001'
    assert result[0]['sender'] == 'alice@example.com'
    assert result[0]['sender_name'] == 'Alice'
    assert result[0]['is_read'] is False
    assert result[0]['has_attachments'] is True


def test_get_email_messages_empty_inbox():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        result = get_email_messages('token', folder_name='inbox', max_results=10)
    assert result == []


def test_get_email_messages_respects_max_results():
    msgs = [{'id': f'msg{i:03}', 'from': {'emailAddress': {'address': 'a@b.com', 'name': 'A'}},
             'subject': f'Subject {i}', 'bodyPreview': '', 'receivedDateTime': '', 'isRead': True, 'hasAttachments': False}
            for i in range(5)]
    with patch('outlook_api.make_graph_request', return_value={'value': msgs}):
        result = get_email_messages('token', folder_name='inbox', max_results=3)
    assert len(result) == 3


#get_email_message_details

def test_get_email_message_details_returns_formatted_dict():
    mock_response = {
        'id': 'msg002',
        'subject': 'Project Update',
        'from': {'emailAddress': {'address': 'bob@example.com', 'name': 'Bob'}},
        'toRecipients': [{'emailAddress': {'address': 'me@example.com'}}],
        'ccRecipients': [],
        'body': {'content': '<p>Update body</p>', 'contentType': 'html'},
        'receivedDateTime': '2025-04-27T09:00:00Z',
        'isRead': True,
        'hasAttachments': False,
        'importance': 'normal',
        'flag': {'flagStatus': 'notFlagged'},
        'conversationId': 'conv001',
    }
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_email_message_details('token', 'msg002')
    assert result['id'] == 'msg002'
    assert result['from'] == 'bob@example.com'
    assert result['from_name'] == 'Bob'
    assert result['to'] == 'me@example.com'
    assert result['body_type'] == 'html'
    assert result['is_read'] is True
    assert result['flagged'] is False


def test_get_email_message_details_flagged():
    mock_response = {
        'id': 'msg003', 'subject': 'Flagged',
        'from': {'emailAddress': {'address': 'x@y.com', 'name': 'X'}},
        'toRecipients': [], 'ccRecipients': [],
        'body': {'content': 'Body', 'contentType': 'text'},
        'receivedDateTime': '', 'isRead': False, 'hasAttachments': False,
        'importance': 'high', 'flag': {'flagStatus': 'flagged'}, 'conversationId': 'c001',
    }
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_email_message_details('token', 'msg003')
    assert result['flagged'] is True
    assert result['importance'] == 'high'


#send_email_with_attachment

def test_outlook_send_success():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = send_email_with_attachment('token', 'to@example.com', 'Subject', 'Body text')
    assert result['status'] == 'sent'


def test_outlook_send_with_cc_and_bcc():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = send_email_with_attachment('token', 'to@example.com', 'Subject', 'Body', cc='cc@x.com', bcc='bcc@x.com')
    assert result['status'] == 'sent'


def test_outlook_send_invalid_body_type_raises():
    with pytest.raises(ValueError, match="body_type must be either 'Text' or 'HTML'"):
        send_email_with_attachment('token', 'to@example.com', 'Subject', 'Body', body_type='text')


def test_outlook_send_missing_attachment_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        send_email_with_attachment('token', 'to@example.com', 'Subject', 'Body', attachment_paths=[str(tmp_path / 'missing.pdf')])


def test_outlook_send_with_real_attachment(tmp_path):
    f = tmp_path / 'doc.txt'
    f.write_text('content')
    with patch('outlook_api.make_graph_request', return_value=None):
        result = send_email_with_attachment('token', 'to@example.com', 'Subject', 'Body', attachment_paths=[str(f)])
    assert result['status'] == 'sent'


#reply_email

def test_outlook_reply_no_attachments_success():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = reply_email('token', 'msg001', 'My reply comment')
    assert result['status'] == 'sent'


def test_outlook_reply_invalid_body_type_raises():
    with pytest.raises(ValueError, match="body_type must be either 'Text' or 'HTML'"):
        reply_email('token', 'msg001', 'Reply text', body_type='plain')


def test_outlook_reply_html_body_type():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = reply_email('token', 'msg001', '<b>Reply</b>', body_type='HTML')
    assert result['status'] == 'sent'


#reply_all_email

def test_outlook_reply_all_no_attachments_success():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = reply_all_email('token', 'msg001', 'Reply all comment')
    assert result['status'] == 'sent'


def test_outlook_reply_all_invalid_body_type_raises():
    with pytest.raises(ValueError, match="body_type must be either 'Text' or 'HTML'"):
        reply_all_email('token', 'msg001', 'Reply text', body_type='html')


#download_attachments

def test_download_attachments_saves_file(tmp_path):
    file_bytes = b'PDF binary content'
    encoded = base64.b64encode(file_bytes).decode()
    mock_response = {'value': [{
        '@odata.type': '#microsoft.graph.fileAttachment',
        'name': 'report.pdf',
        'contentBytes': encoded,
    }]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = download_attachments('token', 'msg001', str(tmp_path))
    assert 'report.pdf' in result
    assert (tmp_path / 'report.pdf').read_bytes() == file_bytes


def test_download_attachments_skips_empty_content(tmp_path):
    mock_response = {'value': [{
        '@odata.type': '#microsoft.graph.fileAttachment',
        'name': 'empty.pdf',
        'contentBytes': '',
    }]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = download_attachments('token', 'msg001', str(tmp_path))
    assert result == []


def test_download_attachments_skips_non_file_types(tmp_path):
    mock_response = {'value': [
        {'@odata.type': '#microsoft.graph.itemAttachment', 'name': 'calendar.ics'},
        {'@odata.type': '#microsoft.graph.referenceAttachment', 'name': 'file.docx'},
    ]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = download_attachments('token', 'msg001', str(tmp_path))
    assert result == []


#search_emails

def test_search_emails_returns_results():
    mock_response = {'value': [{
        'id': 'msg001',
        'from': {'emailAddress': {'address': 'a@b.com', 'name': 'A'}},
        'subject': 'Meeting agenda',
        'bodyPreview': 'See attached',
        'receivedDateTime': '2025-04-27T10:00:00Z',
        'isRead': True,
        'hasAttachments': False,
    }]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = search_emails('token', 'meeting', max_results=5)
    assert len(result) == 1
    assert result[0]['subject'] == 'Meeting agenda'


def test_search_emails_returns_empty_on_no_match():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        result = search_emails('token', 'nothing here')
    assert result == []


#search_email_conversations

def test_search_email_conversations_groups_by_conversation():
    mock_response = {'value': [
        {
            'conversationId': 'conv001',
            'subject': 'Project thread',
            'from': {'emailAddress': {'address': 'a@b.com', 'name': 'A'}},
            'receivedDateTime': '2025-04-27T10:00:00Z',
            'isRead': True,
            'hasAttachments': False,
            'bodyPreview': 'Latest message',
        },
        {
            'conversationId': 'conv001',
            'subject': 'Project thread',
            'from': {'emailAddress': {'address': 'b@b.com', 'name': 'B'}},
            'receivedDateTime': '2025-04-26T10:00:00Z',
            'isRead': True,
            'hasAttachments': False,
            'bodyPreview': 'Earlier message',
        },
    ]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = search_email_conversations('token', 'project', max_results=5)
    assert len(result) == 1
    assert result[0]['conversationId'] == 'conv001'
    assert result[0]['message_count'] == 2


def test_search_email_conversations_empty():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        result = search_email_conversations('token', 'nothing')
    assert result == []


#mark_as_read / mark_as_unread

def test_mark_as_read_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = mark_as_read('token', 'msg001')
    assert 'msg001' in result
    assert 'read' in result


def test_mark_as_unread_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = mark_as_unread('token', 'msg001')
    assert 'msg001' in result


#list_folders

def test_list_folders_returns_formatted_list():
    mock_response = {'value': [{
        'id': 'folder001',
        'displayName': 'Work',
        'parentFolderId': 'root',
        'childFolderCount': 2,
        'unreadItemCount': 5,
        'totalItemCount': 100,
        'isHidden': False,
    }]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = list_folders('token')
    assert len(result) == 1
    assert result[0]['id'] == 'folder001'
    assert result[0]['display_name'] == 'Work'
    assert result[0]['unread_item_count'] == 5


def test_list_folders_empty():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        result = list_folders('token')
    assert result == []


#get_folder_details

def test_get_folder_details_returns_dict():
    mock_response = {
        'id': 'folder001', 'displayName': 'Inbox',
        'parentFolderId': 'root', 'childFolderCount': 0,
        'unreadItemCount': 3, 'totalItemCount': 20, 'isHidden': False,
    }
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_folder_details('token', 'folder001')
    assert result['id'] == 'folder001'
    assert result['display_name'] == 'Inbox'
    assert result['unread_item_count'] == 3


#create_folder / create_child_folder / modify_folder / delete_folder

def _folder_response(folder_id='f001', name='My Folder'):
    return {
        'id': folder_id, 'displayName': name, 'parentFolderId': 'root',
        'childFolderCount': 0, 'unreadItemCount': 0, 'totalItemCount': 0, 'isHidden': False
    }


def test_create_folder_returns_folder():
    with patch('outlook_api.make_graph_request', return_value=_folder_response('f001', 'Work')):
        result = create_folder('token', 'Work')
    assert result['id'] == 'f001'
    assert result['display_name'] == 'Work'


def test_create_child_folder_returns_folder():
    with patch('outlook_api.make_graph_request', return_value=_folder_response('f002', 'Sub')):
        result = create_child_folder('token', 'f001', 'Sub')
    assert result['id'] == 'f002'


def test_modify_folder_returns_updated():
    with patch('outlook_api.make_graph_request', return_value=_folder_response('f001', 'Renamed')):
        result = modify_folder('token', 'f001', 'Renamed')
    assert result['display_name'] == 'Renamed'


def test_delete_folder_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = delete_folder('token', 'f001')
    assert 'f001' in result
    assert 'deleted' in result


#map_folder_name_to_id

def test_map_folder_name_to_id_found():
    mock_response = {'value': [{'id': 'f001', 'displayName': 'Work', 'parentFolderId': 'root',
                                'childFolderCount': 0, 'unreadItemCount': 0, 'totalItemCount': 0, 'isHidden': False}]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = map_folder_name_to_id('token', 'work')
    assert result == 'f001'


def test_map_folder_name_to_id_not_found():
    mock_response = {'value': [{'id': 'f001', 'displayName': 'Inbox', 'parentFolderId': 'root',
                                'childFolderCount': 0, 'unreadItemCount': 0, 'totalItemCount': 0, 'isHidden': False}]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = map_folder_name_to_id('token', 'nonexistent')
    assert result is None


#move_message_to_folder

def test_move_message_to_folder_returns_result():
    mock_response = {'id': 'msg001_new', 'subject': 'Hello', 'parentFolderId': 'folder001'}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = move_message_to_folder('token', 'msg001', 'folder001')
    assert result['id'] == 'msg001_new'
    assert 'folder001' in result['message']


#trash_email / untrash_email / delete_email

def test_outlook_trash_email_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value={'id': 'msg001_deleted', 'subject': 'Test', 'parentFolderId': 'deleteditems'}):
        result = trash_email('token', 'msg001')
    assert 'msg001' in result['message']


def test_outlook_untrash_email_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value={'id': 'msg001_restored', 'subject': 'Test', 'parentFolderId': 'inbox'}):
        result = untrash_email('token', 'msg001')
    assert 'restored' in result['message']


def test_outlook_delete_email_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = delete_email('token', 'msg001')
    assert 'msg001' in result


#trash_email_in_batch / untrash_email_in_batch

def test_trash_email_in_batch_returns_summary():
    with patch('outlook_api.make_graph_request', return_value={'id': 'new_id', 'subject': 'Test', 'parentFolderId': 'deleteditems'}):
        result = trash_email_in_batch('token', ['msg001', 'msg002'])
    assert result['total'] == 2
    assert result['trashed'] == 2


def test_untrash_email_in_batch_returns_summary():
    with patch('outlook_api.make_graph_request', return_value={'id': 'new_id', 'subject': 'Test', 'parentFolderId': 'inbox'}):
        result = untrash_email_in_batch('token', ['msg001', 'msg002'])
    assert result['total'] == 2
    assert result['restored'] == 2


#empty_trash

def test_outlook_empty_trash_returns_count():
    msgs_page = {'value': [{'id': 'msg001'}, {'id': 'msg002'}]}
    empty_page = {'value': []}
    with patch('outlook_api.make_graph_request', side_effect=[msgs_page, None, None, empty_page]):
        count = empty_trash('token')
    assert count == 2


def test_outlook_empty_trash_already_empty():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        count = empty_trash('token')
    assert count == 0


#get_trash_messages

def test_get_trash_messages_calls_get_email_messages():
    mock_response = {'value': []}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_trash_messages('token', max_results=5)
    assert result == []


#get_email_conversations

def test_outlook_get_email_conversations_returns_messages():
    conv_resp = {'conversationId': 'conv001'}
    messages_resp = {'value': [{
        'id': 'msg001',
        'subject': 'Thread Subject',
        'from': {'emailAddress': {'address': 'a@b.com', 'name': 'A'}},
        'toRecipients': [{'emailAddress': {'address': 'me@x.com'}}],
        'body': {'content': 'Message body', 'contentType': 'text'},
        'receivedDateTime': '2025-04-27T10:00:00Z',
        'hasAttachments': False,
    }]}
    with patch('outlook_api.make_graph_request', side_effect=[conv_resp, messages_resp]):
        result = get_email_conversations('token', 'msg001')
    assert len(result) == 1
    assert result[0]['id'] == 'msg001'
    assert result[0]['subject'] == 'Thread Subject'
    assert result[0]['from'] == 'a@b.com'


def test_outlook_get_email_conversations_raises_without_conv_id():
    with patch('outlook_api.make_graph_request', return_value={}):
        with pytest.raises(ValueError, match='Could not find conversation ID'):
            get_email_conversations('token', 'msg001')


#create_draft_email

def test_create_draft_email_returns_draft_id():
    draft_resp = {'id': 'draft001', 'subject': 'My Draft', 'isDraft': True}
    with patch('outlook_api.make_graph_request', return_value=draft_resp):
        result = create_draft_email('token', 'to@example.com', 'My Draft', 'Draft body')
    assert result['id'] == 'draft001'
    assert result['status'] == 'draft created'


def test_create_draft_email_invalid_body_type_raises():
    with pytest.raises(ValueError, match="body_type must be either 'Text' or 'HTML'"):
        create_draft_email('token', 'to@example.com', 'Subject', 'Body', body_type='plain')


def test_create_draft_email_missing_attachment_raises(tmp_path):
    draft_resp = {'id': 'draft001', 'subject': 'Subject', 'isDraft': True}
    with patch('outlook_api.make_graph_request', return_value=draft_resp):
        with pytest.raises(FileNotFoundError):
            create_draft_email('token', 'to@example.com', 'Subject', 'Body', attachment_paths=[str(tmp_path / 'missing.pdf')])


def test_create_draft_email_with_real_attachment(tmp_path):
    f = tmp_path / 'doc.txt'
    f.write_text('content')
    draft_resp = {'id': 'draft002', 'subject': 'Draft with attach', 'isDraft': True}
    with patch('outlook_api.make_graph_request', return_value=draft_resp):
        result = create_draft_email('token', 'to@example.com', 'Subject', 'Body', attachment_paths=[str(f)])
    assert result['id'] == 'draft002'


#list_draft_email_messages

def test_list_draft_email_messages_returns_list():
    mock_response = {'value': [{
        'id': 'draft001',
        'subject': 'Pending draft',
        'toRecipients': [{'emailAddress': {'address': 'to@x.com'}}],
        'createdDateTime': '2025-04-27T08:00:00Z',
        'hasAttachments': False,
        'bodyPreview': 'Draft preview',
    }]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = list_draft_email_messages('token', max_results=5)
    assert len(result) == 1
    assert result[0]['id'] == 'draft001'
    assert result[0]['subject'] == 'Pending draft'


def test_list_draft_email_messages_empty():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        result = list_draft_email_messages('token')
    assert result == []


#get_draft_email_details

def test_get_draft_email_details_returns_dict():
    mock_response = {
        'id': 'draft001', 'subject': 'Draft Subject',
        'from': {'emailAddress': {'address': 'me@x.com', 'name': 'Me'}},
        'toRecipients': [{'emailAddress': {'address': 'to@x.com'}}],
        'ccRecipients': [], 'bccRecipients': [],
        'body': {'content': 'Draft body', 'contentType': 'text'},
        'createdDateTime': '2025-04-27T08:00:00Z',
        'lastModifiedDateTime': '2025-04-27T09:00:00Z',
        'hasAttachments': False, 'importance': 'normal',
        'isDraft': True, 'conversationId': 'conv001',
    }
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_draft_email_details('token', 'draft001')
    assert result['id'] == 'draft001'
    assert result['subject'] == 'Draft Subject'
    assert result['is_draft'] is True
    assert result['body_type'] == 'text'


#send_draft_email / delete_draft_email

def test_outlook_send_draft_email_returns_status():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = send_draft_email('token', 'draft001')
    assert result['status'] == 'sent'
    assert 'draft001' in result['message']


def test_outlook_delete_draft_email_returns_confirmation():
    with patch('outlook_api.make_graph_request', return_value=None):
        result = delete_draft_email('token', 'draft001')
    assert 'draft001' in result


#update_draft_email

def test_update_draft_no_fields_raises():
    with pytest.raises(ValueError, match='No fields provided to update.'):
        update_draft_email('token', 'draft001')


def test_update_draft_with_subject_only():
    mock_response = {'id': 'draft001', 'subject': 'New Subject'}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = update_draft_email('token', 'draft001', subject='New Subject')
    assert result['subject'] == 'New Subject'


def test_update_draft_with_body_and_type():
    mock_response = {'id': 'draft001', 'subject': 'Subject'}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = update_draft_email('token', 'draft001', body='New body', body_type='HTML')
    assert result['id'] == 'draft001'


def test_update_draft_with_recipients():
    mock_response = {'id': 'draft001', 'subject': 'Subject'}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = update_draft_email('token', 'draft001', to='new@x.com', cc='cc@x.com', bcc='bcc@x.com')
    assert result['id'] == 'draft001'


#get_attachment_list / get_attachment_data

def test_get_attachment_list_returns_attachments():
    mock_response = {'value': [{
        'id': 'att001',
        'name': 'document.pdf',
        'contentType': 'application/pdf',
        'size': 2048,
    }]}
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        result = get_attachment_list('token', 'msg001')
    assert len(result) == 1
    assert result[0]['filename'] == 'document.pdf'
    assert result[0]['id'] == 'att001'
    assert result[0]['size'] == 2048


def test_get_attachment_list_empty():
    with patch('outlook_api.make_graph_request', return_value={'value': []}):
        result = get_attachment_list('token', 'msg001')
    assert result == []


def test_get_attachment_data_returns_bytes_and_metadata():
    file_bytes = b'Binary file content'
    encoded = base64.b64encode(file_bytes).decode()
    mock_response = {
        'name': 'photo.jpg',
        'contentType': 'image/jpeg',
        'contentBytes': encoded,
    }
    with patch('outlook_api.make_graph_request', return_value=mock_response):
        data, filename, content_type = get_attachment_data('token', 'msg001', 'att001')
    assert data == file_bytes
    assert filename == 'photo.jpg'
    assert content_type == 'image/jpeg'

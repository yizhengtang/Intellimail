#teams_api.py
#Microsoft Teams API functions — list chats, read messages, send messages, list joined teams.
#Functions return Teams-native field names — the frontend has its own Teams types (TeamsChat,
#TeamsMessage) and its own UI. No normalization to email shapes happens here.

import os
import httpx
from dotenv import load_dotenv
from Teams.teams_auth import get_access_token, MS_GRAPH_BASE_ENDPOINT

load_dotenv()

TEAMS_SCOPES = ['Chat.ReadWrite', 'Team.ReadBasic.All']


#Initialize Teams service by acquiring an access token with Teams-specific scopes.
#On first run, opens a browser window — user logs in with their school account.
#On subsequent runs, uses the stored refresh token silently.
def initialize_teams_service():
    app_id = os.getenv('MICROSOFT_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')

    if not app_id or not client_secret:
        raise ValueError("MICROSOFT_CLIENT_ID or MICROSOFT_CLIENT_SECRET not found in environment variables.")

    return get_access_token(app_id, client_secret, TEAMS_SCOPES)


#Helper to make authenticated requests to Microsoft Graph API.
#Same pattern as outlook_api.py — reused here to keep the Teams module self-contained.
def make_graph_request(access_token, endpoint, method='GET', params=None, json_data=None):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    url = f'{MS_GRAPH_BASE_ENDPOINT}{endpoint}'

    with httpx.Client(timeout=30.0) as client:
        if method == 'GET':
            response = client.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = client.post(url, headers=headers, json=json_data)

        response.raise_for_status()
        return response.json() if response.text else None


#Returns a list of the user's chats (1:1 and group) using Teams-native field names.
#$expand=lastMessagePreview fetches the last message preview in the same call — avoids N+1 requests.
#For 1:1 chats, topic is null from the API — derived as "Chat with {sender_name}" instead.
def list_chats(access_token, max_results=10):
    params = {
        '$top': min(50, max_results),
        '$expand': 'lastMessagePreview',
        '$orderby': 'lastMessagePreview/createdDateTime desc'
    }

    result = make_graph_request(access_token, 'me/chats', params=params)
    chats = []

    for chat in result.get('value', []):
        preview = chat.get('lastMessagePreview') or {}
        sender_info = preview.get('from') or {}

        #from.user.displayName covers member messages; from.application.displayName covers bot messages.
        sender_name = (
            (sender_info.get('user') or {}).get('displayName')
            or (sender_info.get('application') or {}).get('displayName')
            or 'Unknown'
        )

        #Group chats have a topic; 1:1 chats return topic: null so we derive one.
        topic = chat.get('topic') or f'Chat with {sender_name}'

        chats.append({
            'id': chat['id'],
            'topic': topic,
            'chat_type': chat.get('chatType', 'oneOnOne'),
            'last_sender': sender_name,
            'last_message': preview.get('body', {}).get('content', ''),
            'last_message_time': preview.get('createdDateTime', ''),
            'member_count': 0,      # fetching members requires an extra call per chat — not worth the cost
        })

    return chats[:max_results]


#Returns all messages in a chat using Teams-native field names.
#Messages are ordered newest-first (createdDateTime desc).
def get_chat_messages(access_token, chat_id, max_results=50):
    params = {
        '$top': min(50, max_results),
        '$orderby': 'createdDateTime desc'
    }

    result = make_graph_request(access_token, f'chats/{chat_id}/messages', params=params)
    messages = []

    for msg in result.get('value', []):
        sender_info = msg.get('from') or {}
        sender_name = (
            (sender_info.get('user') or {}).get('displayName')
            or (sender_info.get('application') or {}).get('displayName')
            or 'Unknown'
        )

        body = msg.get('body', {})

        messages.append({
            'id': msg['id'],
            'sender_name': sender_name,
            'content': body.get('content', ''),
            'content_type': body.get('contentType', 'text'),
            'created_at': msg.get('createdDateTime', ''),
            'has_attachments': len(msg.get('attachments', [])) > 0,
        })

    return messages[:max_results]


#Sends a plain-text message to an existing chat.
#Graph API returns 201 Created with no response body — this function returns None.
def send_chat_message(access_token, chat_id, body):
    json_data = {
        'body': {
            'content': body,
            'contentType': 'text'
        }
    }
    make_graph_request(access_token, f'chats/{chat_id}/messages', method='POST', json_data=json_data)


#Returns a list of Teams the user has joined.
#Used by the Teams sidebar section to show which teams the user belongs to.
def list_joined_teams(access_token):
    params = {'$select': 'id,displayName'}
    result = make_graph_request(access_token, 'me/joinedTeams', params=params)

    return [
        {'id': team['id'], 'name': team['displayName']}
        for team in result.get('value', [])
    ]

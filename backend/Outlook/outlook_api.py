import os
import httpx
from dotenv import load_dotenv
from MS_Graph import get_access_token, MS_GRAPH_BASE_ENDPOINT

load_dotenv()

#Initialize Outlook service by getting access token
def initialize_outlook_service(scopes=['https://graph.microsoft.com/Mail.ReadWrite']):
    app_id = os.getenv('MICROSOFT_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')

    if not app_id or not client_secret:
        raise ValueError("MICROSOFT_APP_ID or MICROSOFT_CLIENT_SECRET not found in environment variables.")

    access_token = get_access_token(app_id, client_secret, scopes)
    return access_token

#Helper function to make requests to Microsoft Graph API
def make_graph_request(access_token, endpoint, method='GET', params=None, json_data=None):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    url = f'{MS_GRAPH_BASE_ENDPOINT}{endpoint}'

    with httpx.Client() as client:
        if method == 'GET':
            response = client.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = client.post(url, headers=headers, json=json_data)
        elif method == 'DELETE':
            response = client.delete(url, headers=headers)
        elif method == 'PATCH':
            response = client.patch(url, headers=headers, json=json_data)

        response.raise_for_status()
        return response.json() if response.text else None

#Function to get email messages from Outlook
#This function WILL ONLY fetch basic email info (id, sender, subject, receivedDateTime, isRead)
def get_email_messages(access_token, folder_name='inbox', max_results=10):
    messages = []

    #Build the endpoint - use folder name if provided
    endpoint = f'me/mailFolders/{folder_name}/messages'

    #Parameters for the request
    params = {
        #Maximum number of results to fetch
        '$top': min(50, max_results),
        '$select': 'id,from,subject,receivedDateTime,isRead',
        '$orderby': 'receivedDateTime desc'
    }

    #Pagination loop
    while True:
        result = make_graph_request(access_token, endpoint, params=params)

        #Extract and format the message data
        for msg in result.get('value', []):
            messages.append({
                'id': msg.get('id'),
                'sender': msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown sender'),
                'sender_name': msg.get('from', {}).get('emailAddress', {}).get('name', ''),
                'subject': msg.get('subject', 'No subject'),
                'received_time': msg.get('receivedDateTime', 'No date available'),
                'is_read': msg.get('isRead', False)
            })

        #Check for next page
        next_link = result.get('@odata.nextLink')
        if not next_link or len(messages) >= max_results:
            break

        #Update endpoint for next page (nextLink is a full URL)
        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        #parameters can be set to none since they are already included in the nextlink
        params = None

    return messages[:max_results] if max_results else messages

#This function will retrieve the full details of a specific email
def get_email_message_details(access_token, message_id):
    endpoint = f'me/messages/{message_id}'

    #Request full message details
    params = {
        '$select': 'id,subject,from,toRecipients,ccRecipients,body,receivedDateTime,isRead,hasAttachments,importance,flag,conversationId'
    }

    message = make_graph_request(access_token, endpoint, params=params)

    #Extract and format the details similar to Gmail function
    email_details = {
        'id': message.get('id'),
        'subject': message.get('subject', 'No subject'),
        'from': message.get('from', {}).get('emailAddress', {}).get('address', 'Unknown sender'),
        'from_name': message.get('from', {}).get('emailAddress', {}).get('name', ''),
        'to': ', '.join([r.get('emailAddress', {}).get('address', '') for r in message.get('toRecipients', [])]),
        'cc': ', '.join([r.get('emailAddress', {}).get('address', '') for r in message.get('ccRecipients', [])]),
        'body': message.get('body', {}).get('content', '<Text body not available>'),
        'body_type': message.get('body', {}).get('contentType', 'text'),
        'date': message.get('receivedDateTime', 'No date available'),
        'is_read': message.get('isRead', False),
        'has_attachments': message.get('hasAttachments', False),
        'importance': message.get('importance', 'normal'),
        'flagged': message.get('flag', {}).get('flagStatus', 'notFlagged') == 'flagged',
        'conversation_id': message.get('conversationId', message_id)
    }

    return email_details


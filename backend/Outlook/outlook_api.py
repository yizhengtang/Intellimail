import os
import base64
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

#This function will send an email with attachments using Microsoft Graph API.
#Unlike Gmail which uses MIME format, Graph API uses JSON structure with separate fields.
def send_email_with_attachment(access_token, to, subject, body, body_type='Text', cc=None, bcc=None, attachment_paths=None):
    #Validate body_type (Graph API uses 'Text' or 'HTML', not lowercase)
    if body_type not in ['Text', 'HTML']:
        raise ValueError("body_type must be either 'Text' or 'HTML'")

    #Helper function to convert email string or list to Graph API recipient format
    def format_recipients(recipients):
        if not recipients:
            return []

        #Convert single string to list
        if isinstance(recipients, str):
            recipients = [recipients]

        #Format each recipient as Graph API expects
        return [{"emailAddress": {"address": email.strip()}} for email in recipients]

    #Build the message structure
    message = {
        "subject": subject,
        "body": {
            "contentType": body_type,
            "content": body
        },
        "toRecipients": format_recipients(to)
    }

    #Add CC recipients if provided
    if cc:
        message["ccRecipients"] = format_recipients(cc)

    #Add BCC recipients if provided
    if bcc:
        message["bccRecipients"] = format_recipients(bcc)

    #Process attachments if provided
    if attachment_paths:
        attachments = []

        for attachment_path in attachment_paths:
            #Check if file exists
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment file '{attachment_path}' not found.")

            #Get filename
            filename = os.path.basename(attachment_path)

            #Read file and encode to base64
            with open(attachment_path, 'rb') as file:
                file_content = file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            #Create attachment object in Graph API format
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentBytes": encoded_content
            }

            attachments.append(attachment)

        #Add attachments to message
        message["attachments"] = attachments

    #Build the request body
    request_body = {
        "message": message,
        "saveToSentItems": True
    }

    #Send the email using Graph API
    endpoint = 'me/sendMail'
    response = make_graph_request(access_token, endpoint, method='POST', json_data=request_body)

    return {"status": "sent", "message": "Email sent successfully"}

#This function will download all attachments from a specific email message.
def download_attachments(access_token, message_id, download_dir):
    """
    Download all attachments from a specific email message.

    Args:
        access_token: OAuth2 access token
        message_id: The ID of the message to download attachments from
        download_dir: Directory path to save attachments

    Returns:
        List of downloaded filenames
    """

    #Ensure the download directory exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    #Get all attachments for the message
    #Note: Don't use $select with contentBytes as it may cause 400 errors
    endpoint = f'me/messages/{message_id}/attachments'

    result = make_graph_request(access_token, endpoint)

    attachments = result.get('value', [])
    downloaded_files = []

    #Process each attachment
    for attachment in attachments:
        attachment_type = attachment.get('@odata.type', '')
        filename = attachment.get('name', 'unnamed_attachment')

        #Handle file attachments (most common)
        if attachment_type == '#microsoft.graph.fileAttachment':
            #Get base64 encoded content
            content_bytes = attachment.get('contentBytes', '')

            if content_bytes:
                #Decode base64 content
                file_data = base64.b64decode(content_bytes)

                #Create full file path
                file_path = os.path.join(download_dir, filename)

                #Write to file
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                downloaded_files.append(filename)
                print(f"Attachment '{filename}' downloaded to '{file_path}'")
            else:
                print(f"Warning: Attachment '{filename}' has no content")

        #Handle item attachments (embedded emails, calendar items, etc.)
        elif attachment_type == '#microsoft.graph.itemAttachment':
            print(f"Skipping item attachment '{filename}' (embedded message/item)")

        #Handle reference attachments (cloud files)
        elif attachment_type == '#microsoft.graph.referenceAttachment':
            print(f"Skipping reference attachment '{filename}' (cloud file link)")

        else:
            print(f"Unknown attachment type: {attachment_type}")

    return downloaded_files

#This function will download attachments from all messages in a conversation thread.
def download_attachments_all(access_token, message_id, download_dir):
    #First, get the conversation ID from the provided messageID
    endpoint = f'me/messages/{message_id}'
    params = {'$select': 'conversationId'}

    message = make_graph_request(access_token, endpoint, params=params)
    conversation_id = message.get('conversationId')

    if not conversation_id:
        raise ValueError(f"Could not find conversation ID for message {message_id}")

    #Get messages in this conversation
    endpoint = 'me/messages'
    params = {
        '$select': 'id,subject,hasAttachments,conversationId,receivedDateTime',
        '$top': 50, 
        '$orderby': 'receivedDateTime desc'
    }

    all_messages = []

    #Fetch messages and filter by conversationId client-side
    while True:
        result = make_graph_request(access_token, endpoint, params=params)
        fetched_messages = result.get('value', [])

        #Filter for messages with matching conversationId
        matching_messages = [msg for msg in fetched_messages if msg.get('conversationId') == conversation_id]
        all_messages.extend(matching_messages)

        #If we found messages in this conversation, continue fetching to get all of them
        next_link = result.get('@odata.nextLink')
        if not next_link or (len(matching_messages) == 0 and len(all_messages) > 0):
            break

        #Update endpoint for pagination
        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    #Sort by received time (ascending - oldest first)
    messages = sorted(all_messages, key=lambda x: x.get('receivedDateTime', ''))

    print(f"Found {len(messages)} messages in conversation")

    all_downloaded_files = []

    #Download attachments from each message that has attachments
    for msg in messages:
        msg_id = msg.get('id')
        has_attachments = msg.get('hasAttachments', False)

        if has_attachments:
            print(f"Downloading attachments from message: {msg.get('subject', 'No subject')}")
            downloaded = download_attachments(access_token, msg_id, download_dir)
            all_downloaded_files.extend(downloaded)
        else:
            print(f"Skipping message (no attachments): {msg.get('subject', 'No subject')}")

    return {
        'conversation_id': conversation_id,
        'total_files': len(all_downloaded_files),
        'downloaded_files': all_downloaded_files
    }

#This function will search for individual emails by query.
def search_emails(access_token, query, max_results=5):
    messages = []
    endpoint = 'me/messages'

    #Microsoft Graph API uses $search parameter for searching
    params = {
        '$search': f'"{query}"',
        '$select': 'id,from,subject,receivedDateTime,isRead,hasAttachments',
        '$top': min(50, max_results) if max_results else 50
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
                'is_read': msg.get('isRead', False),
                'has_attachments': msg.get('hasAttachments', False)
            })

        #Check for next page
        next_link = result.get('@odata.nextLink')
        if not next_link or (max_results and len(messages) >= max_results):
            break

        #Update endpoint for next page
        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    return messages[:max_results] if max_results else messages

#This function will search for email conversations (threads) by query.
def search_email_conversations(access_token, query, max_results=5):
    #Search messages first
    endpoint = 'me/messages'
    params = {
        '$search': f'"{query}"',
        '$select': 'conversationId,subject,from,receivedDateTime',
        '$top': 50
    }

    all_messages = []

    #Fetch messages matching the search query
    while True:
        result = make_graph_request(access_token, endpoint, params=params)
        fetched_messages = result.get('value', [])
        all_messages.extend(fetched_messages)

        #Check if we need more messages
        next_link = result.get('@odata.nextLink')
        if not next_link or len(all_messages) >= (max_results * 10):  # Fetch extra to find unique conversations
            break

        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    #Group by conversationId to get unique conversations
    conversations_dict = {}
    for msg in all_messages:
        conv_id = msg.get('conversationId')
        if conv_id and conv_id not in conversations_dict:
            conversations_dict[conv_id] = {
                'conversationId': conv_id,
                'subject': msg.get('subject', 'No subject'),
                'from': msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
                'from_name': msg.get('from', {}).get('emailAddress', {}).get('name', ''),
                'received_time': msg.get('receivedDateTime', 'No date')
            }

    #Convert to list and limit to max_results
    conversations = list(conversations_dict.values())
    return conversations[:max_results] if max_results else conversations


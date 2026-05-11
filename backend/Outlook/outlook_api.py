import os
import base64
import httpx
from dotenv import load_dotenv
from MS_Graph import get_access_token, MS_GRAPH_BASE_ENDPOINT

load_dotenv()

#Initialize Outlook service by getting access token
def initialize_outlook_service(scopes=['https://graph.microsoft.com/Mail.ReadWrite', 'User.Read']):
    app_id = os.getenv('MICROSOFT_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')

    if not app_id or not client_secret:
        raise ValueError("MICROSOFT_APP_ID or MICROSOFT_CLIENT_SECRET not found in environment variables.")

    access_token = get_access_token(app_id, client_secret, scopes)
    return access_token

#Helper function to make requests to Microsoft Graph API
def make_graph_request(access_token, endpoint, method='GET', params=None, json_data=None, extra_headers=None):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    #Merge any extra headers (e.g. Prefer header for body content type)
    if extra_headers:
        headers.update(extra_headers)

    url = f'{MS_GRAPH_BASE_ENDPOINT}{endpoint}'

    with httpx.Client(timeout=30.0) as client:
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

#Maps display names and Gmail label names to Graph API well-known folder names.
#Graph API only accepts well-known names (e.g. 'sentitems') or GUIDs in the URL path.
#Display names like 'Sent Items' or Gmail labels like 'SENT' cause a 400 Bad Request.
OUTLOOK_FOLDER_MAP = {
    'inbox': 'inbox',
    'sent items': 'sentitems',
    'sent': 'sentitems',
    'sentitems': 'sentitems',
    'deleted items': 'deleteditems',
    'deleteditems': 'deleteditems',
    'trash': 'deleteditems',
    'drafts': 'drafts',
    'draft': 'drafts',
    'junk email': 'junkemail',
    'junkemail': 'junkemail',
    'junk': 'junkemail',
    'spam': 'junkemail',
    'archive': 'archive',
    'outbox': 'outbox',
}

#Function to get email messages from Outlook
#This function WILL ONLY fetch basic email info (id, sender, subject, receivedDateTime, isRead)
def get_email_messages(access_token, folder_name='inbox', max_results=10):
    messages = []

    #Translate display names and cross-provider label names to Graph API well-known names.
    #GUIDs (from the folder list) pass through unchanged since they won't match any map key.
    folder_id = OUTLOOK_FOLDER_MAP.get(folder_name.lower(), folder_name)
    endpoint = f'me/mailFolders/{folder_id}/messages'

    #Parameters for the request
    params = {
        #Maximum number of results to fetch
        '$top': min(50, max_results),
        '$select': 'id,from,subject,receivedDateTime,isRead,hasAttachments,bodyPreview',
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
                'snippet': msg.get('bodyPreview', ''),
                'received_time': msg.get('receivedDateTime', 'No date available'),
                'is_read': msg.get('isRead', False),
                'has_attachments': msg.get('hasAttachments', False)
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

#This function will reply to the sender of a specific email message.
def reply_email(access_token, message_id, comment, body_type='Text', attachment_paths=None):
    #Validate body_type (Graph API uses 'Text' or 'HTML')
    if body_type not in ['Text', 'HTML']:
        raise ValueError("body_type must be either 'Text' or 'HTML'")

    if attachment_paths:
        #When attachments are needed, use createReply to produce a draft first,
        #then attach files, then send the draft.
        #POST /me/messages/{id}/createReply returns a new draft message object.
        create_endpoint = f'me/messages/{message_id}/createReply'
        json_data = {
            "comment": comment
        }
        draft = make_graph_request(access_token, create_endpoint, method='POST', json_data=json_data)
        draft_id = draft.get('id')

        #Update the draft body content type if HTML was requested.
        #createReply preserves the original body type; patch it if we need a different type.
        if body_type == 'HTML':
            patch_endpoint = f'me/messages/{draft_id}'
            patch_data = {
                "body": {
                    "contentType": body_type,
                    "content": comment
                }
            }
            make_graph_request(access_token, patch_endpoint, method='PATCH', json_data=patch_data)

        #Add each attachment to the draft via POST /me/messages/{draft_id}/attachments
        for attachment_path in attachment_paths:
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment file '{attachment_path}' not found.")

            filename = os.path.basename(attachment_path)

            with open(attachment_path, 'rb') as file:
                file_content = file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentBytes": encoded_content
            }

            attachment_endpoint = f'me/messages/{draft_id}/attachments'
            make_graph_request(access_token, attachment_endpoint, method='POST', json_data=attachment)

        #Send the draft via POST /me/messages/{draft_id}/send
        send_endpoint = f'me/messages/{draft_id}/send'
        make_graph_request(access_token, send_endpoint, method='POST')

    else:
        #No attachments - use the direct reply endpoint.
        #POST /me/messages/{id}/reply with a comment sends the reply immediately.
        reply_endpoint = f'me/messages/{message_id}/reply'
        json_data = {
            "comment": comment
        }
        make_graph_request(access_token, reply_endpoint, method='POST', json_data=json_data)

    return {"status": "sent", "message": "Reply sent successfully"}

#This function will reply to all recipients of a specific email message (sender + all To/Cc).
def reply_all_email(access_token, message_id, comment, body_type='Text', attachment_paths=None):
    #Validate body_type (Graph API uses 'Text' or 'HTML')
    if body_type not in ['Text', 'HTML']:
        raise ValueError("body_type must be either 'Text' or 'HTML'")

    if attachment_paths:
        #When attachments are needed, use createReplyAll to produce a draft first,
        #then attach files, then send the draft.
        #POST /me/messages/{id}/createReplyAll returns a new draft message object.
        create_endpoint = f'me/messages/{message_id}/createReplyAll'
        json_data = {
            "comment": comment
        }
        draft = make_graph_request(access_token, create_endpoint, method='POST', json_data=json_data)
        draft_id = draft.get('id')

        #Update the draft body content type if HTML was requested.
        if body_type == 'HTML':
            patch_endpoint = f'me/messages/{draft_id}'
            patch_data = {
                "body": {
                    "contentType": body_type,
                    "content": comment
                }
            }
            make_graph_request(access_token, patch_endpoint, method='PATCH', json_data=patch_data)

        #Add each attachment to the draft via POST /me/messages/{draft_id}/attachments
        for attachment_path in attachment_paths:
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment file '{attachment_path}' not found.")

            filename = os.path.basename(attachment_path)

            with open(attachment_path, 'rb') as file:
                file_content = file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentBytes": encoded_content
            }

            attachment_endpoint = f'me/messages/{draft_id}/attachments'
            make_graph_request(access_token, attachment_endpoint, method='POST', json_data=attachment)

        #Send the draft via POST /me/messages/{draft_id}/send
        send_endpoint = f'me/messages/{draft_id}/send'
        make_graph_request(access_token, send_endpoint, method='POST')

    else:
        #No attachments - use the direct replyAll endpoint.
        #POST /me/messages/{id}/replyAll sends to all recipients immediately.
        reply_all_endpoint = f'me/messages/{message_id}/replyAll'
        json_data = {
            "comment": comment
        }
        make_graph_request(access_token, reply_all_endpoint, method='POST', json_data=json_data)

    return {"status": "sent", "message": "Reply-all sent successfully"}

#This function will download all attachments from a specific email message.
def download_attachments(access_token, message_id, download_dir):
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
        '$select': 'id,from,subject,receivedDateTime,isRead,hasAttachments,bodyPreview',
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
                'snippet': msg.get('bodyPreview', ''),
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
#This is different from what I have in gmail, as microsoft graph doesnt have thread endpoint to get conversation, so my approach is to search messages and then group by conversation ID.
def search_email_conversations(access_token, query, max_results=5):
    #Search messages first
    endpoint = 'me/messages'
    params = {
        '$search': f'"{query}"',
        '$select': 'conversationId,subject,from,receivedDateTime,isRead,hasAttachments,bodyPreview',
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
        #Fetch extra to find unique conversations
        if not next_link or len(all_messages) >= (max_results * 10): 
            break

        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    #Group by conversationId and aggregate metadata from all messages in each conversation.
    conversations_dict = {}
    for msg in all_messages:
        conv_id = msg.get('conversationId')
        if not conv_id:
            continue

        if conv_id not in conversations_dict:
            conversations_dict[conv_id] = {
                'conversationId': conv_id,
                'subject': msg.get('subject', 'No subject'),
                'messages': []
            }

        conversations_dict[conv_id]['messages'].append(msg)

    #Build the final result by aggregating each conversation's messages
    conversations = []
    for conv in conversations_dict.values():
        msgs = conv['messages']

        #Sort by receivedDateTime descending to get the most recent message first
        msgs.sort(key=lambda m: m.get('receivedDateTime', ''), reverse=True)
        latest = msgs[0]

        conversations.append({
            'conversationId': conv['conversationId'],
            'subject': conv['subject'],
            'from': latest.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
            'from_name': latest.get('from', {}).get('emailAddress', {}).get('name', ''),
            'snippet': latest.get('bodyPreview', ''),
            'received_time': latest.get('receivedDateTime', 'No date'),
            'message_count': len(msgs),
            'is_read': all(m.get('isRead', False) for m in msgs),
            'has_attachments': any(m.get('hasAttachments', False) for m in msgs),
        })

    return conversations[:max_results] if max_results else conversations

#This function will mark an email as read.
def mark_as_read(access_token, message_id):
    endpoint = f'me/messages/{message_id}'
    json_data = {"isRead": True}

    make_graph_request(access_token, endpoint, method='PATCH', json_data=json_data)

    return f'Message {message_id} marked as read.'

#This function will mark an email as unread.
def mark_as_unread(access_token, message_id):
    endpoint = f'me/messages/{message_id}'
    json_data = {"isRead": False}

    make_graph_request(access_token, endpoint, method='PATCH', json_data=json_data)

    return f'Message {message_id} marked as unread.'

#This function will list all mail folders.
def list_folders(access_token, include_hidden=False):
    endpoint = 'me/mailFolders'

    #Add parameter to include hidden folders if requested
    params = {}
    if include_hidden:
        params['includeHiddenFolders'] = 'true'

    folders = []

    #Pagination loop
    while True:
        result = make_graph_request(access_token, endpoint, params=params if params else None)

        #Extract and format folder data
        for folder in result.get('value', []):
            folders.append({
                'id': folder.get('id'),
                'display_name': folder.get('displayName'),
                'parent_folder_id': folder.get('parentFolderId'),
                'child_folder_count': folder.get('childFolderCount', 0),
                'unread_item_count': folder.get('unreadItemCount', 0),
                'total_item_count': folder.get('totalItemCount', 0),
                'is_hidden': folder.get('isHidden', False)
            })

        #Check for next page
        next_link = result.get('@odata.nextLink')
        if not next_link:
            break

        #Update endpoint for next page
        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    return folders

#This function will get details for a specific folder by ID.
def get_folder_details(access_token, folder_id):
    endpoint = f'me/mailFolders/{folder_id}'

    folder = make_graph_request(access_token, endpoint)

    folder_details = {
        'id': folder.get('id'),
        'display_name': folder.get('displayName'),
        'parent_folder_id': folder.get('parentFolderId'),
        'child_folder_count': folder.get('childFolderCount', 0),
        'unread_item_count': folder.get('unreadItemCount', 0),
        'total_item_count': folder.get('totalItemCount', 0),
        'is_hidden': folder.get('isHidden', False)
    }

    return folder_details

#This function will create a new mail folder.
def create_folder(access_token, display_name, is_hidden=False):
    endpoint = 'me/mailFolders'

    json_data = {
        'displayName': display_name
    }

    #Only include isHidden if set to True (default is False)
    if is_hidden:
        json_data['isHidden'] = True

    created_folder = make_graph_request(access_token, endpoint, method='POST', json_data=json_data)

    return {
        'id': created_folder.get('id'),
        'display_name': created_folder.get('displayName'),
        'parent_folder_id': created_folder.get('parentFolderId'),
        'child_folder_count': created_folder.get('childFolderCount', 0),
        'unread_item_count': created_folder.get('unreadItemCount', 0),
        'total_item_count': created_folder.get('totalItemCount', 0),
        'is_hidden': created_folder.get('isHidden', False)
    }

#This function will create a child folder under a parent folder.
def create_child_folder(access_token, parent_folder_id, display_name, is_hidden=False):
    endpoint = f'me/mailFolders/{parent_folder_id}/childFolders'

    json_data = {
        'displayName': display_name
    }

    #Only include isHidden if set to True (default is False)
    if is_hidden:
        json_data['isHidden'] = True

    created_folder = make_graph_request(access_token, endpoint, method='POST', json_data=json_data)

    return {
        'id': created_folder.get('id'),
        'display_name': created_folder.get('displayName'),
        'parent_folder_id': created_folder.get('parentFolderId'),
        'child_folder_count': created_folder.get('childFolderCount', 0),
        'unread_item_count': created_folder.get('unreadItemCount', 0),
        'total_item_count': created_folder.get('totalItemCount', 0),
        'is_hidden': created_folder.get('isHidden', False)
    }

#This function will modify/update an existing folder's display name.
def modify_folder(access_token, folder_id, display_name):
    endpoint = f'me/mailFolders/{folder_id}'

    json_data = {
        'displayName': display_name
    }

    updated_folder = make_graph_request(access_token, endpoint, method='PATCH', json_data=json_data)

    return {
        'id': updated_folder.get('id'),
        'display_name': updated_folder.get('displayName'),
        'parent_folder_id': updated_folder.get('parentFolderId'),
        'child_folder_count': updated_folder.get('childFolderCount', 0),
        'unread_item_count': updated_folder.get('unreadItemCount', 0),
        'total_item_count': updated_folder.get('totalItemCount', 0),
        'is_hidden': updated_folder.get('isHidden', False)
    }

#This function will delete a folder by ID.
def delete_folder(access_token, folder_id):
    endpoint = f'me/mailFolders/{folder_id}'

    make_graph_request(access_token, endpoint, method='DELETE')

    return f'Folder with ID {folder_id} deleted successfully.'

#Helper function to map folder name to ID.
def map_folder_name_to_id(access_token, folder_name):
    folders = list_folders(access_token, include_hidden=True)

    for folder in folders:
        if folder['display_name'].lower() == folder_name.lower():
            return folder['id']

    return None

#This function will move a message to a different folder.
def move_message_to_folder(access_token, message_id, destination_id):
    endpoint = f'me/messages/{message_id}/move'

    json_data = {
        'destinationId': destination_id
    }

    moved_message = make_graph_request(access_token, endpoint, method='POST', json_data=json_data)

    return {
        'id': moved_message.get('id'),
        'subject': moved_message.get('subject', 'No subject'),
        'parent_folder_id': moved_message.get('parentFolderId'),
        'message': f'Message moved to folder {destination_id}'
    }

#This function will trash a specific email by moving it to the Deleted Items folder.
def trash_email(access_token, message_id):
    endpoint = f'me/messages/{message_id}/move'

    json_data = {
        'destinationId': 'deleteditems'
    }

    moved_message = make_graph_request(access_token, endpoint, method='POST', json_data=json_data)

    return {
        'id': moved_message.get('id'),
        'message': f'Message {message_id} moved to trash.'
    }

#This function allows trashing multiple emails by batch.
def trash_email_in_batch(access_token, message_ids):
    results = []

    for message_id in message_ids:
        try:
            result = trash_email(access_token, message_id)
            results.append({'id': message_id, 'status': 'trashed', 'new_id': result['id']})
        except Exception as e:
            results.append({'id': message_id, 'status': 'failed', 'error': str(e)})

    return {
        'total': len(message_ids),
        'trashed': len([r for r in results if r['status'] == 'trashed']),
        'results': results
    }

#This function will untrash a specific email by moving it back to the Inbox.
#destination_folder can be 'inbox' (default) or any other folder ID/well-known name.
def untrash_email(access_token, message_id, destination_folder='inbox'):
    endpoint = f'me/messages/{message_id}/move'

    json_data = {
        'destinationId': destination_folder
    }

    moved_message = make_graph_request(access_token, endpoint, method='POST', json_data=json_data)

    return {
        'id': moved_message.get('id'),
        'message': f'Message restored from trash to {destination_folder}.'
    }

#This function will untrash multiple emails by batch.
def untrash_email_in_batch(access_token, message_ids, destination_folder='inbox'):
    results = []

    for message_id in message_ids:
        try:
            result = untrash_email(access_token, message_id, destination_folder)
            results.append({'id': message_id, 'status': 'restored', 'new_id': result['id']})
        except Exception as e:
            results.append({'id': message_id, 'status': 'failed', 'error': str(e)})

    return {
        'total': len(message_ids),
        'restored': len([r for r in results if r['status'] == 'restored']),
        'results': results
    }

#This function permanently deletes an email.
def delete_email(access_token, message_id):
    endpoint = f'me/messages/{message_id}'

    make_graph_request(access_token, endpoint, method='DELETE')

    return f'Message {message_id} deleted.'

#This function will empty the trash (Deleted Items folder).
#Permanently deletes all messages in the deleteditems folder.
def empty_trash(access_token):
    total_deleted = 0
    endpoint = 'me/mailFolders/deleteditems/messages'

    params = {
        '$select': 'id',
        '$top': 50
    }

    while True:
        result = make_graph_request(access_token, endpoint, params=params)
        messages = result.get('value', [])

        if not messages:
            break

        #Delete each message
        for msg in messages:
            try:
                delete_email(access_token, msg['id'])
                total_deleted += 1
            except Exception as e:
                print(f"Error deleting message {msg['id']}: {e}")

        #Check for next page
        next_link = result.get('@odata.nextLink')
        if not next_link:
            break

        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    return total_deleted

#This function will get all messages from the trash (Deleted Items folder).
def get_trash_messages(access_token, max_results=10):
    return get_email_messages(access_token, folder_name='deleteditems', max_results=max_results)

#This function will get the entire conversation of an email by message ID.
#Returns the full details of each message in the conversation, sorted by date (oldest first).
def get_email_conversations(access_token, message_id):
    #First, get the conversation ID from the provided message
    endpoint = f'me/messages/{message_id}'
    params = {'$select': 'conversationId'}

    message = make_graph_request(access_token, endpoint, params=params)
    conversation_id = message.get('conversationId')

    if not conversation_id:
        raise ValueError(f"Could not find conversation ID for message {message_id}")

    #Fetch all messages in this conversation using $filter for server-side filtering
    #This is more efficient than fetching all messages and filtering client-side
    endpoint = 'me/messages'
    params = {
        '$filter': f"conversationId eq '{conversation_id}'",
        '$select': 'id,subject,from,toRecipients,body,receivedDateTime,hasAttachments',
        '$top': 50
    }

    #Use Prefer header to request plain text body instead of HTML, by defailt it returns HTML
    prefer_headers = {'Prefer': 'outlook.body-content-type="text"'}

    all_messages = []

    #Pagination loop to get all messages in the conversation
    while True:
        result = make_graph_request(access_token, endpoint, params=params, extra_headers=prefer_headers)
        all_messages.extend(result.get('value', []))

        next_link = result.get('@odata.nextLink')
        if not next_link:
            break

        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    #Sort by oldest first.
    all_messages.sort(key=lambda x: x.get('receivedDateTime', ''))

    #Process each message into a consistent format
    processed_messages = []
    for msg in all_messages:
        processed_messages.append({
            'id': msg.get('id'),
            'subject': msg.get('subject', 'No subject'),
            'from': msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown sender'),
            'from_name': msg.get('from', {}).get('emailAddress', {}).get('name', ''),
            'to': ', '.join([r.get('emailAddress', {}).get('address', '') for r in msg.get('toRecipients', [])]),
            'body': msg.get('body', {}).get('content', '<Text body not available>'),
            'date': msg.get('receivedDateTime', 'No date available'),
            'has_attachments': msg.get('hasAttachments', False)
        })

    return processed_messages

#This function will create a draft email message.
#Unlike Gmail which uses MIME format, Graph API uses JSON structure with separate fields.
def create_draft_email(access_token, to, subject, body, body_type='Text', cc=None, bcc=None, attachment_paths=None):
    #Validate body_type (Graph API uses 'Text' or 'HTML')
    if body_type not in ['Text', 'HTML']:
        raise ValueError("body_type must be either 'Text' or 'HTML'")

    #Helper function to convert email string or list to Graph API recipient format
    def format_recipients(recipients):
        if not recipients:
            return []
        if isinstance(recipients, str):
            recipients = [recipients]
        return [{"emailAddress": {"address": email.strip()}} for email in recipients]

    #Build the draft message structure
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

    #Create the draft first via POST /me/messages
    endpoint = 'me/messages'
    created_draft = make_graph_request(access_token, endpoint, method='POST', json_data=message)

    draft_id = created_draft.get('id')

    #If attachment paths are provided, upload them to the draft message
    #Attachments are added separately after draft creation using POST /me/messages/{id}/attachments
    if attachment_paths:
        for attachment_path in attachment_paths:
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment file '{attachment_path}' not found.")

            filename = os.path.basename(attachment_path)

            with open(attachment_path, 'rb') as file:
                file_content = file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentBytes": encoded_content
            }

            attachment_endpoint = f'me/messages/{draft_id}/attachments'
            make_graph_request(access_token, attachment_endpoint, method='POST', json_data=attachment)

    #Return the created draft details
    return {
        'id': draft_id,
        'subject': created_draft.get('subject', 'No subject'),
        'status': 'draft created'
    }

#This function will list all draft email messages from the Drafts folder.
def list_draft_email_messages(access_token, max_results=10):
    messages = []
    endpoint = 'me/mailFolders/drafts/messages'

    params = {
        '$top': min(50, max_results),
        '$select': 'id,subject,toRecipients,createdDateTime,hasAttachments,bodyPreview',
        '$orderby': 'createdDateTime desc'
    }

    #Pagination loop
    while True:
        result = make_graph_request(access_token, endpoint, params=params)

        for msg in result.get('value', []):
            #Extract the first recipient's email address if available
            to_recipients = msg.get('toRecipients', [])
            to_address = to_recipients[0].get('emailAddress', {}).get('address', '') if to_recipients else ''

            messages.append({
                'id': msg.get('id'),
                'subject': msg.get('subject', 'No subject'),
                'to': to_address,
                'created_time': msg.get('createdDateTime', 'No date available'),
                'has_attachments': msg.get('hasAttachments', False),
                'body_preview': msg.get('bodyPreview', '')
            })

        #Check for next page
        next_link = result.get('@odata.nextLink')
        if not next_link or len(messages) >= max_results:
            break

        endpoint = next_link.replace(MS_GRAPH_BASE_ENDPOINT, '')
        params = None

    return messages[:max_results] if max_results else messages

#This function will get the full details of a specific draft email by ID.
def get_draft_email_details(access_token, draft_id):
    endpoint = f'me/messages/{draft_id}'

    params = {
        '$select': 'id,subject,from,toRecipients,ccRecipients,bccRecipients,body,createdDateTime,lastModifiedDateTime,hasAttachments,importance,isDraft,conversationId'
    }

    message = make_graph_request(access_token, endpoint, params=params)

    draft_details = {
        'id': message.get('id'),
        'subject': message.get('subject', 'No subject'),
        'from': message.get('from', {}).get('emailAddress', {}).get('address', 'Unknown sender'),
        'from_name': message.get('from', {}).get('emailAddress', {}).get('name', ''),
        'to': ', '.join([r.get('emailAddress', {}).get('address', '') for r in message.get('toRecipients', [])]),
        'cc': ', '.join([r.get('emailAddress', {}).get('address', '') for r in message.get('ccRecipients', [])]),
        'bcc': ', '.join([r.get('emailAddress', {}).get('address', '') for r in message.get('bccRecipients', [])]),
        'body': message.get('body', {}).get('content', '<Text body not available>'),
        'body_type': message.get('body', {}).get('contentType', 'text'),
        'created_time': message.get('createdDateTime', 'No date available'),
        'last_modified_time': message.get('lastModifiedDateTime', 'No date available'),
        'has_attachments': message.get('hasAttachments', False),
        'importance': message.get('importance', 'normal'),
        'is_draft': message.get('isDraft', False),
        'conversation_id': message.get('conversationId', draft_id)
    }

    return draft_details

#This function will send a draft email by its message ID.
def send_draft_email(access_token, draft_id):
    endpoint = f'me/messages/{draft_id}/send'

    make_graph_request(access_token, endpoint, method='POST')

    return {'status': 'sent', 'message': f'Draft {draft_id} sent successfully.'}

#This function will delete a draft email by its message ID.
#Uses DELETE /me/messages/{id} endpoint, same as deleting any message.
def delete_draft_email(access_token, draft_id):
    endpoint = f'me/messages/{draft_id}'

    make_graph_request(access_token, endpoint, method='DELETE')

    return f'Draft {draft_id} deleted successfully.'

#This function will update an existing draft email.
def update_draft_email(access_token, draft_id, subject=None, body=None, body_type=None, to=None, cc=None, bcc=None):
    #Helper function to convert email string or list to Graph API recipient format
    def format_recipients(recipients):
        if not recipients:
            return []
        if isinstance(recipients, str):
            recipients = [recipients]
        return [{"emailAddress": {"address": email.strip()}} for email in recipients]

    #Build the update payload with only the fields that are provided
    json_data = {}

    if subject is not None:
        json_data['subject'] = subject

    if body is not None:
        #If body_type is not specified, default to 'Text'
        content_type = body_type if body_type in ['Text', 'HTML'] else 'Text'
        json_data['body'] = {
            'contentType': content_type,
            'content': body
        }

    if to is not None:
        json_data['toRecipients'] = format_recipients(to)

    if cc is not None:
        json_data['ccRecipients'] = format_recipients(cc)

    if bcc is not None:
        json_data['bccRecipients'] = format_recipients(bcc)

    if not json_data:
        raise ValueError("No fields provided to update.")

    endpoint = f'me/messages/{draft_id}'
    updated_draft = make_graph_request(access_token, endpoint, method='PATCH', json_data=json_data)

    return {
        'id': updated_draft.get('id'),
        'subject': updated_draft.get('subject', 'No subject'),
        'status': 'draft updated'
    }

#Returns metadata for every attachment in an email (id, filename, content_type, size).
#Does not fetch file bytes — only the info needed to render the attachment list in the UI.
def get_attachment_list(access_token, message_id):
    endpoint = f'me/messages/{message_id}/attachments'
    params = {'$select': 'id,name,contentType,size'}
    result = make_graph_request(access_token, endpoint, params=params)
    attachments = []
    for att in result.get('value', []):
        attachments.append({
            'id': att.get('id'),
            'filename': att.get('name', 'attachment'),
            'content_type': att.get('contentType', 'application/octet-stream'),
            'size': att.get('size', 0),
        })
    return attachments

#Fetches the raw bytes for a single attachment by its attachment_id.
#Graph API returns contentBytes as standard base64 (not URL-safe like Gmail).
#Returns (bytes, filename, content_type) so the router can stream the file to the browser.
def get_attachment_data(access_token, message_id, attachment_id):
    endpoint = f'me/messages/{message_id}/attachments/{attachment_id}'
    params = {'$select': 'name,contentType,contentBytes'}
    result = make_graph_request(access_token, endpoint, params=params)
    filename = result.get('name', 'attachment')
    content_type = result.get('contentType', 'application/octet-stream')
    data = base64.b64decode(result.get('contentBytes', ''))
    return data, filename, content_type


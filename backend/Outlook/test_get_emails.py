from outlook_api import initialize_outlook_service, get_email_messages, get_email_message_details

# Initialize Outlook service
access_token = initialize_outlook_service()

# Get emails from inbox
emails = get_email_messages(access_token, folder_name='inbox', max_results=1)

print(f"\nFetching details for {len(emails)} emails...\n")

for email in emails:
    # Fetch full details for each email
    details = get_email_message_details(access_token, email['id'])

    print(f"Message ID: {details['id']}")
    print(f"Conversation ID: {details['conversation_id']}")
    print(f"From: {details['from_name']} <{details['from']}>")
    print(f"To: {details['to']}")
    print(f"CC: {details['cc']}")
    print(f"Subject: {details['subject']}")
    print(f"Body Type: {details['body_type']}")
    print(f"Body: {details['body'][:200]}..." if len(details['body']) > 200 else f"Body: {details['body']}")
    print(f"Date: {details['date']}")
    print(f"Read: {details['is_read']}")
    print(f"Has Attachments: {details['has_attachments']}")
    print(f"Importance: {details['importance']}")
    print(f"Flagged: {details['flagged']}")
    print("-" * 80)

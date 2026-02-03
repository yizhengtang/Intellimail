from outlook_api import initialize_outlook_service, get_email_message_details, search_emails, search_email_conversations

access_token = initialize_outlook_service()

query = 'attachment'
emails = search_emails(access_token, query, max_results=5)

print(f"\nFetching details for {len(emails)} emails matching query: '{query}'\n")

for email in emails:
    details = get_email_message_details(access_token, email['id'])

    print(f"Message ID: {details['id']}")
    print(f"Conversation ID: {details['conversation_id']}")
    print(f"From: {details['from_name']} <{details['from']}>")
    print(f"To: {details['to']}")
    print(f"Subject: {details['subject']}")
    print(f"Body: {details['body'][:200]}..." if len(details['body']) > 200 else f"Body: {details['body']}")
    print(f"Date: {details['date']}")
    print(f"Read: {details['is_read']}")
    print(f"Has Attachments: {details['has_attachments']}")
    print(f"Importance: {details['importance']}")
    print(f"Flagged: {details['flagged']}")
    print("-" * 80)

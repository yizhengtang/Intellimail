from outlook_api import initialize_outlook_service, get_email_messages, get_email_conversations

access_token = initialize_outlook_service()

# Get a message ID from the inbox to use for testing
print("Fetching a message from inbox to get its conversation...")
emails = get_email_messages(access_token, folder_name='inbox', max_results=1)

if not emails:
    print("No emails found in inbox.")
else:
    message_id = emails[0]['id']
    print(f"Using email: {emails[0]['subject']}")
    print(f"Message ID: {message_id[:30]}...")
    print("-" * 80)

    print(f"\nFetching full conversation thread...\n")
    conversations = get_email_conversations(access_token, message_id)

    print(f"Found {len(conversations)} message(s) in this conversation:\n")
    for conversation in conversations:
        print(f"Message ID: {conversation['id'][:30]}...")
        print(f"From: {conversation['from_name']} <{conversation['from']}>")
        print(f"To: {conversation['to']}")
        print(f"Subject: {conversation['subject']}")
        print(f"Date: {conversation['date']}")
        print(f"Has Attachments: {conversation['has_attachments']}")
        print(f"Body Preview: {conversation['body'][:200]}...")
        print("-" * 80)

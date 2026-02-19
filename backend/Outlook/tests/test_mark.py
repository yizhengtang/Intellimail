from outlook_api import initialize_outlook_service, get_email_messages, mark_as_read, mark_as_unread, get_email_message_details

# Initialize Outlook service
access_token = initialize_outlook_service()

# Get a test email from inbox
emails = get_email_messages(access_token, folder_name='inbox', max_results=1)

if not emails:
    print("No emails found in inbox!")
    exit()

message_id = emails[0]['id']
print(f"Test email ID: {message_id}")
print(f"Subject: {emails[0]['subject']}")
print("-" * 80)

# Test 1: Mark as unread
print("\nTest 1: Marking email as UNREAD...")
result = mark_as_unread(access_token, message_id)
print(f"✅ {result}")

# Verify the change
details = get_email_message_details(access_token, message_id)
print(f"Status check: isRead = {details['is_read']}")
print("-" * 80)

# Test 2: Mark as read
print("\nTest 2: Marking email as READ...")
result = mark_as_read(access_token, message_id)
print(f"✅ {result}")

# Verify the change
details = get_email_message_details(access_token, message_id)
print(f"Status check: isRead = {details['is_read']}")
print("-" * 80)

print("\n✅ All tests completed successfully!")

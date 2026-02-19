from outlook_api import (
    initialize_outlook_service,
    get_email_messages,
    get_email_message_details,
    trash_email,
    untrash_email,
    get_trash_messages,
    delete_email
)

# Initialize Outlook service
access_token = initialize_outlook_service()

print("=" * 80)
print("OUTLOOK TRASH/UNTRASH TEST")
print("=" * 80)

# Get a test email from inbox
print("\nFetching test email from inbox...")
emails = get_email_messages(access_token, folder_name='inbox', max_results=1)

if not emails:
    print("No emails found in inbox! Please make sure you have at least one email.")
    exit()

message_id = emails[0]['id']
subject = emails[0]['subject']
print(f"Test email ID: {message_id[:30]}...")
print(f"Subject: {subject}")
print("-" * 80)

# Test 1: Trash the email
print("\nTest 1: Moving email to trash (Deleted Items)...")
result = trash_email(access_token, message_id)
new_message_id = result['id']
print(f"Result: {result['message']}")
print(f"New message ID after move: {new_message_id[:30]}...")
print("-" * 80)

# Test 2: Verify email is in trash
print("\nTest 2: Verifying email is in Deleted Items folder...")
trash_messages = get_trash_messages(access_token, max_results=10)
found_in_trash = any(msg['id'] == new_message_id for msg in trash_messages)
if found_in_trash:
    print(f"Email found in Deleted Items folder")
else:
    print("Warning: Email not found in trash (may have different ID after move)")
    # Try to find by subject
    for msg in trash_messages:
        if msg['subject'] == subject:
            print(f"Found email by subject in trash with ID: {msg['id'][:30]}...")
            new_message_id = msg['id']
            break
print("-" * 80)

# Test 3: Untrash the email (restore to inbox)
print("\nTest 3: Restoring email from trash to Inbox...")
result = untrash_email(access_token, new_message_id, 'inbox')
restored_message_id = result['id']
print(f"Result: {result['message']}")
print(f"Restored message ID: {restored_message_id[:30]}...")
print("-" * 80)

# Test 4: Verify email is back in inbox
print("\nTest 4: Verifying email is back in Inbox...")
inbox_emails = get_email_messages(access_token, folder_name='inbox', max_results=10)
found_in_inbox = any(msg['id'] == restored_message_id for msg in inbox_emails)
if found_in_inbox:
    print("Email successfully restored to Inbox")
else:
    print("Warning: Email not found in inbox with expected ID")
    # Try to find by subject
    for msg in inbox_emails:
        if msg['subject'] == subject:
            print(f"Found email by subject in inbox")
            break
print("-" * 80)

# Test 5: Show current trash contents
print("\nTest 5: Current Deleted Items folder contents...")
trash_messages = get_trash_messages(access_token, max_results=5)
print(f"Found {len(trash_messages)} messages in Deleted Items:")
for msg in trash_messages:
    print(f"  - {msg['subject'][:50]}...")
print("-" * 80)

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED!")
print("=" * 80)
print("\nNote: The empty_trash() and delete_email() functions are available but")
print("not tested here to avoid permanent data loss. Use with caution!")

from pathlib import Path
from outlook_api import (
    initialize_outlook_service,
    create_draft_email,
    list_draft_email_messages,
    get_draft_email_details,
    update_draft_email,
    send_draft_email,
    delete_draft_email
)

access_token = initialize_outlook_service()

to_address = "yzhengtang04@gmail.com"
subject = "Test Draft Email from Outlook API"
body = "This is a test draft email created using the Microsoft Graph API."
body_type = 'Text'

attachment_dir = Path('./attachments')
attachment_files = list(attachment_dir.glob('*'))

try:
    # 1. Create a draft email with attachments
    print("=== Creating Draft Email ===")
    draft_response = create_draft_email(
        access_token=access_token,
        to=to_address,
        subject=subject,
        body=body,
        body_type=body_type,
        attachment_paths=attachment_files
    )
    print(f"Draft created with ID: {draft_response['id']}")
    print(f"Subject: {draft_response['subject']}")
    print(f"Status: {draft_response['status']}")

    draft_id = draft_response['id']

    # 2. List all draft emails
    print("\n=== Listing Draft Emails ===")
    drafts = list_draft_email_messages(access_token, max_results=5)
    for draft in drafts:
        print(f"  ID: {draft['id'][:30]}...")
        print(f"  Subject: {draft['subject']}")
        print(f"  To: {draft['to']}")
        print(f"  Created: {draft['created_time']}")
        print(f"  Has Attachments: {draft['has_attachments']}")
        print()

    # 3. Get draft email details
    print("=== Getting Draft Details ===")
    details = get_draft_email_details(access_token, draft_id)
    print(f"Subject: {details['subject']}")
    print(f"From: {details['from']}")
    print(f"To: {details['to']}")
    print(f"Body Type: {details['body_type']}")
    print(f"Is Draft: {details['is_draft']}")
    print(f"Has Attachments: {details['has_attachments']}")
    print(f"Importance: {details['importance']}")

    # 4. Update the draft email
    print("\n=== Updating Draft Email ===")
    updated = update_draft_email(
        access_token=access_token,
        draft_id=draft_id,
        subject="Updated Test Draft Email from Outlook API",
        body="This draft has been updated using the Microsoft Graph API."
    )
    print(f"Updated Subject: {updated['subject']}")
    print(f"Status: {updated['status']}")

    # 5. Delete the draft email (comment out if you want to send it instead)
    # print("\n=== Deleting Draft Email ===")
    # delete_response = delete_draft_email(access_token, draft_id)
    # print(delete_response)

    # 6. Send draft email (uncomment to test sending instead of deleting)
    print("\n=== Sending Draft Email ===")
    send_response = send_draft_email(access_token, draft_id)
    print(f"Status: {send_response['status']}")
    print(f"Message: {send_response['message']}")

except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid value: {e}")
except Exception as e:
    print(f"Error: {e}")

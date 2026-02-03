from pathlib import Path
from outlook_api import send_email_with_attachment, initialize_outlook_service

access_token = initialize_outlook_service()

to_address = "yzhengtang04@gmail.com"
subject = "Test Email with Attachment from Outlook API"
body = "This is a test email sent from the Microsoft Graph API with an attachment."
body_type = 'Text'

attachment_dir = Path('./attachments')
attachment_files = list(attachment_dir.glob('*'))

try:
    # Send email with attachments
    response = send_email_with_attachment(
        access_token=access_token,
        to=to_address,
        subject=subject,
        body=body,
        body_type=body_type,
        attachment_paths=attachment_files
    )

    print("=Email sent successfully")
    print(f"Response: {response}")
    print(f"Sent to: {to_address}")
    print(f"Subject: {subject}")
    print(f"Attachments: {len(attachment_files)} file(s)")

except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid value: {e}")
except Exception as e:
    print(f"Failed to send email: {e}")

from outlook_api import initialize_outlook_service, get_email_messages

#Initialize the Outlook service and get access token
access_token = initialize_outlook_service()

#Get emails from inbox
emails = get_email_messages(access_token, folder_name='inbox', max_results=5)

#Print the results
print(f'Found {len(emails)} emails:\n')

for email in emails:
    print(f"From: {email['sender_name']} <{email['sender']}>")
    print(f"Subject: {email['subject']}")
    print(f"Received: {email['received_time']}")
    print(f"Read: {email['is_read']}")
    print('-' * 50)

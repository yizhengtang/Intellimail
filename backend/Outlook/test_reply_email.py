from outlook_api import initialize_outlook_service, get_email_messages, get_email_message_details, reply_email, reply_all_email

access_token = initialize_outlook_service()

# Get a message from inbox to reply to
print("Fetching a message from inbox...")
emails = get_email_messages(access_token, folder_name='inbox', max_results=1)

if not emails:
    print("No emails found in inbox.")
else:
    message_id = emails[0]['id']
    details = get_email_message_details(access_token, message_id)
    print(f"Replying to: {details['subject']}")
    print(f"From: {details['from']}")
    print(f"To: {details['to']}")
    print("-" * 80)

    # Test 1: Reply to sender only
    print("\n=== Test 1: Reply to Sender ===")
    try:
        response = reply_email(
            access_token,
            message_id,
            comment="This is a test reply sent using the Microsoft Graph API.",
            body_type='Text'
        )
        print(f"Reply sent successfully!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Reply all (uncomment to test)
    # print("\n=== Test 2: Reply All ===")
    # try:
    #     response = reply_all_email(
    #         access_token,
    #         message_id,
    #         comment="This is a test reply-all sent using the Microsoft Graph API.",
    #         body_type='Text'
    #     )
    #     print(f"Reply-all sent successfully!")
    #     print(f"Response: {response}")
    # except Exception as e:
    #     print(f"Error: {e}")

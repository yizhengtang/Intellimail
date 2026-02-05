from outlook_api import(
    initialize_outlook_service,
    list_folders,
    get_folder_details,
    create_folder,
    create_child_folder,
    modify_folder,
    delete_folder,
    map_folder_name_to_id,
    move_message_to_folder,
    get_email_messages
)

# Initialize Outlook service
access_token = initialize_outlook_service()

print("=" * 80)
print("OUTLOOK FOLDER MANAGEMENT TEST")
print("=" * 80)

# Test 1: List all folders
print("\nTest 1: Listing all mail folders...")
folders = list_folders(access_token)
print(f"Found {len(folders)} folders:")
for folder in folders:
    print(f"  - {folder['display_name']} (ID: {folder['id'][:20]}...)")
    print(f"    Total items: {folder['total_item_count']}, Unread: {folder['unread_item_count']}")
print("-" * 80)


print("\nTest 2: Getting details for Inbox folder...")
inbox_id = map_folder_name_to_id(access_token, 'Inbox')
if inbox_id:
    inbox_details = get_folder_details(access_token, inbox_id)
    print(f"Inbox Details:")
    print(f"  Display Name: {inbox_details['display_name']}")
    print(f"  Total Items: {inbox_details['total_item_count']}")
    print(f"  Unread Items: {inbox_details['unread_item_count']}")
    print(f"  Child Folders: {inbox_details['child_folder_count']}")
else:
    print("Could not find Inbox folder")
print("-" * 80)

print("\nTest 3: Creating a new folder 'Test Folder'...")
try:
    new_folder = create_folder(access_token, 'Test Folder')
    print(f"Created folder:")
    print(f"  ID: {new_folder['id']}")
    print(f"  Display Name: {new_folder['display_name']}")
    test_folder_id = new_folder['id']
except Exception as e:
    print(f"Error creating folder: {e}")
    test_folder_id = None
print("-" * 80)

# Test 4: Create a child folder under the test folder
if test_folder_id:
    print("\nTest 4: Creating a child folder 'Test Subfolder' under 'Test Folder'...")
    try:
        child_folder = create_child_folder(access_token, test_folder_id, 'Test Subfolder')
        print(f"Created child folder:")
        print(f"  ID: {child_folder['id']}")
        print(f"  Display Name: {child_folder['display_name']}")
        print(f"  Parent Folder ID: {child_folder['parent_folder_id']}")
        child_folder_id = child_folder['id']
    except Exception as e:
        print(f"Error creating child folder: {e}")
        child_folder_id = None
    print("-" * 80)

    # Test 5: Modify the folder name
    print("\nTest 5: Renaming 'Test Folder' to 'Renamed Test Folder'...")
    try:
        updated_folder = modify_folder(access_token, test_folder_id, 'Renamed Test Folder')
        print(f"Updated folder:")
        print(f"  ID: {updated_folder['id']}")
        print(f"  New Display Name: {updated_folder['display_name']}")
    except Exception as e:
        print(f"Error modifying folder: {e}")
    print("-" * 80)

    # Test 6: Map folder name to ID
    print("\nTest 6: Testing map_folder_name_to_id function...")
    found_id = map_folder_name_to_id(access_token, 'Renamed Test Folder')
    if found_id:
        print(f"Found folder 'Renamed Test Folder' with ID: {found_id[:30]}...")
    else:
        print("Could not find folder by name")
    print("-" * 80)

    # Test 7: Move a message to the test folder (optional - only if emails exist)
    print("\nTest 7: Testing move_message_to_folder function...")
    emails = get_email_messages(access_token, folder_name='inbox', max_results=1)
    if emails:
        message_id = emails[0]['id']
        print(f"Moving email '{emails[0]['subject']}' to 'Renamed Test Folder'...")
        try:
            result = move_message_to_folder(access_token, message_id, test_folder_id)
            print(f"Message moved successfully!")
            print(f"  New Message ID: {result['id'][:30]}...")

            # Move it back to inbox
            print("Moving message back to Inbox...")
            move_message_to_folder(access_token, result['id'], 'inbox')
            print("Message moved back to Inbox.")
        except Exception as e:
            print(f"Error moving message: {e}")
    else:
        print("No emails in inbox to test move function")
    print("-" * 80)

    # Test 8: Delete the child folder first, then the parent folder
    print("\nTest 8: Cleaning up - deleting test folders...")
    try:
        if child_folder_id:
            result = delete_folder(access_token, child_folder_id)
            print(f"Child folder deleted: {result}")

        result = delete_folder(access_token, test_folder_id)
        print(f"Parent folder deleted: {result}")
    except Exception as e:
        print(f"Error deleting folder: {e}")
    print("-" * 80)

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED!")
print("=" * 80)

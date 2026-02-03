import pathlib as Path
from outlook_api import download_attachments, download_attachments_all, initialize_outlook_service

access_token = initialize_outlook_service()

message_id = 'AQMkADAwATNiZmYAZC1mZgAwOC04NGE2LTAwAi0wMAoARgAAA9-KmWvKEd5MsayCgFBF58QHAKPwXXDR4U1Cqf5QD2ZvCyEAAAIBDAAAAKPwXXDR4U1Cqf5QD2ZvCyEAB4kjh6oAAAA='
download_dir = Path.Path('./downloads')

download_attachments(access_token, message_id, download_dir)

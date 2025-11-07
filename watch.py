import os

from googleapiclient.discovery import build

CREDENTIALS = os.environ.get('CREDENTIALS')
service = build('drive', 'v3', credentials=CREDENTIALS)

def create_watch():
    channel_id = '0f44c8af-cc03-4583-9f9e-e8a72dc8a060'
    callback_url = "127.0.0.1:8080"
    body = {
        'id': channel_id,
        'type': "webhook",
        'address': callback_url,
    }
    start_page_token_response = service.changes().getStartPageToken().execute()
    start_page_token = start_page_token_response.get('startPageToken')

    with open('page_token.txt', 'w') as f:
        f.write(start_page_token)
    
    response = service.changes().watch(body=body, pageToken=start_page_token).execute()
    return response

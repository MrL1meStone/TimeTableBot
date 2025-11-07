import os

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE_DATA = os.environ.get("CREDENTIALS")
SERVICE_ACCOUNT_FILE = json.loads(SERVICE_ACCOUNT_FILE_DATA)
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def create_watch():
    channel_id = '0f44c8af-cc03-4583-9f9e-e8a72dc8a060'
    callback_url = "127.0.0.1:8080"
    body = {
        'id': channel_id,
        'type': 'webhook',
        'address': callback_url, # Можно доп. параметры
    }
    start_page_token_response = service.changes().getStartPageToken().execute()
    start_page_token = start_page_token_response.get('startPageToken')

    with open('page_token.txt', 'w') as f:
        f.write(start_page_token)
    
    response = service.changes().watch(body=body, pageToken=start_page_token).execute()
    return response

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = "coral-firefly-472118-d4-0e2e192450f3.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def create_watch():
    channel_id = '0f44c8af-cc03-4583-9f9e-e8a72dc8a060'
    callback_url = "адрес сервера"
    body = {
        'id': channel_id,
        'type': "webhook',
        'address': callback_url, # Можно доп. параметры
    }
    start_page_token_response = service.changes().getStartPageToken().execute()
    start_page_token = start_page_token_response.get('startPageToken')

    with open('page_token.txt', 'w') as f:
        f.write(start_page_token) # Туда его
    
    response = service.changes().watch(body=body, pageToken=start_page_token).execute()
    return response

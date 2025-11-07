from fastapi import FastAPI, Request, Header
from googleapiclient.discovery import build
from google.oauth2 import service_account
from aiogram import Bot
import uvicorn
import json
import os

# SERVICE_ACCOUNT_FILE = "coral-firefly-472118-d4-0e2e192450f3.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER__GOOGLE_DRIVE_ID = os.environ.get("FOLDER_ID")
SERVICE_ACCOUNT_FILE_DATA = os.environ.get("CREDENTIALS")
SERVICE_ACCOUNT_FILE = json.loads(SERVICE_ACCOUNT_FILE_DATA)
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
service = build('drive', 'v3', credentials=credentials)
chat_id = 'your_chat_id'

def process_notification(payload):
    try:
        with open('files.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
        results = service.files().list(

        q=f"'{FOLDER__GOOGLE_DRIVE_ID}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'", fields="files(id, name, modifiedTime)").execute()

        files = results.get('files', [])
        for file in files:
            data[file['id']] = {'name': file['name'], 'modifiedTime': file['modifiedTime']}
        with open('files.json', 'w', encoding='utf-8') as file:
            json.dump(data, file)
    
    final_answer = None
    
    if payload.get('removed'):  #  Проверка на удаленный файл
         needed_file_id = payload["fileId"]
         new_data = {}
         for ID in data.keys():
              if ID != needed_file_id:
                   new_data[ID] = data[ID]
         data = new_data

    else:
         file_metadata = service.files().get(fileId=payload["fileId"], fields='id, name, mimeType, modifiedTime').execute()
         file_name = file_metadata.get('name')
         time = file_metadata.get('modifiedTime')
         if not(payload["fileId"] in data.keys()): # Проверка на добавленный файл
              data[payload["fileId"]] = {'name': file_name, 'modifiedTime':time}
              final_answer = f'Новый файл {file_name} был добавлен на диск'
         else:
              if data[payload["fileId"]]['modifiedTime'] != time: # Проверка на измененный файл
                   final_answer = f'Файл {file_name} был изменен'
                   data[payload["fileId"]]['modifiedTime'] = time

    with open('files.json', 'w', encoding='utf-8') as file:
         json.dump(data, file)
    return final_answer

app = FastAPI()

@app.post('/notifications')
async def handle_notification(
    request: Request,
    resource_state: str = Header(None, alias='X-Goog-Resource-State')
):
    payload = await request.json()
    print("Внимание! Получено уведомление")

    changes = process_notification(payload)
    if changes:
         for chat in chat_id:
              await bot.send_message(chat, f"Внимание, расписание обновлено: {changes}")

    return {'status': 'ok'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)  # Не финальный хост

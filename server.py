from fastapi import FastAPI, Request, Header
from googleapiclient.discovery import build
from aiogram import Bot
import uvicorn
import json
import os

FOLDER_ID = os.environ.get("FOLDER_ID")
CREDENTIALS = os.environ.get('CREDENTIALS')
TOKEN = os.environ.get("BOT_TOKEN")

service = build('drive', 'v3', credentials=CREDENTIALS)
bot = Bot(token=TOKEN)

def process_notification(payload):
    try:
        with open('files.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
            fields="files(id, name, modifiedTime)").execute()
        files = results.get('files', [])
        for file in files:
            data[file['id']] = {'name': file['name'], 'modifiedTime': file['modifiedTime']}
        with open('files.json', 'w', encoding='utf-8') as file:
            json.dump(data, file)

    final_answer = ''

    if payload.get('removed'):  #  Проверка на удаленный файл
         needed_file_id = payload["fileId"]
         final_answer = f'Файл {data[needed_file_id]["name"]} был удален с диска'
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
    if len(changes) > len('Внимание! Кажется, '):
         for chat in some_func:
              await bot.send_message(chat, f"Внимание! На диске изменение: {changes}")

    return {'status': 'ok'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)  # Не финальный хост


import os
import io
import openpyxl
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
SERVICE_ACCOUNT_FILE = "C:\\Users\\Валентин\\Downloads\\coral-firefly-472118-d4-0e2e192450f3.json"
FOLDER_ID = '1jfQFPUpOuv_tNLyQIoipPVsLQHv_H5UQ'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
def main():
    current_files = []
    try:
        with open('schedule.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
        with open('schedule.json', 'w', encoding='utf-8') as file:
            json.dump(data, file)
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    #  Запрос на получение списка файлов
    results = service.files().list(
    q=f"'{FOLDER_ID}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'", fields="files(id, name)").execute()
    #  Получение списка файлов
    files = results.get('files', [])
    if not files:
        return print("В папке нет XLSX-файлов.")
    # Создание папки
    os.makedirs('downloaded_xlsx', exist_ok=True)
    doc_list = {}
    # Скачивание
    for file in files:
      file_id = file['id']
      file_name = file['name']
      document = {}
      current_files.append(file_name)
      if not(file_name in data):
        request = service.files().get_media(fileId=file_id)
        file_path = os.path.join('downloaded_xlsx', file_name)
        print(f"Скачивание {file_name}...")
        with open(file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Прогресс: {int(status.progress() * 100)}%")
        print(f"{file_name} скачан(а).")
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        for row in sheet.iter_rows():
            rowl = []
            for cell in row:
                if cell.value is not None:
                        rowl.append(cell.value)
            if rowl != []:
                document[row] = rowl
        doc_list[file_name] = list(document.values())
        os.remove(file_path)
    print("Все файлы скачаны.")
    with open('schedule.json', 'w', encoding='utf-8') as file:
            json.dump(current_files, file)
    return doc_list

p = main()
for p1 in p:
    print(p1)
    for p2 in p[p1]:
        print(p2)
        print()

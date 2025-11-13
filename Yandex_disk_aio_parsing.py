import aiohttp
import asyncio
import os
from aiogram import Bot
from aiogram.types import FSInputFile

url_file_check = 'https://cloud-api.yandex.net/v1/disk/public/resources'
public_key = 'https://disk.yandex.ru/d/yAnW2VBU1IfTPQ'
save_dir = "downloaded_jpgs"
token='y0__xD0pMWkCBjVujsgxevcihUw-KTFpAh64k1R7DwSYhNUnD0q59xarXMMKQ'
headers = {
    "Authorization": f"OAuth {token}"
    }
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)

async def download_file(session, href, filename):
    # Функция скачивает бинарный файл filename по ссылке для скачивания href
    file_path = os.path.join(save_dir, filename)
    async with session.get(href) as response:
        if response.status == 200:
            content = await response.read() 
            with open(file_path, 'wb') as f:
                    f.write(content)
            print(f'Файл {filename} скачан')
        else:
                print(f"Ошибка: {response.status}")
                print(await response.text())
                return None
async def get_folder_contents(session, public_key):
    # Функция подробную информацию о всех файлах на диске
    params = {'public_key' : public_key}
    async with session.get(url_file_check, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Ошибка: {response.status}")
                print(await response.text())
                return None
async def get_file_names_with_apload():
    # Функция позволяет получить имена всех файлов на диске в виде списка (для создания кнопок), одновременно скачав их с расширением .jpg
    async with aiohttp.ClientSession() as session:
        result = await get_folder_contents(session, public_key)
        filenames = []
        if result:
            for item in result['_embedded']['items']:
                if item['type'] == 'file':
                    if os.path.splitext(item['name'])[1] in ('.docx', '.txt', '.pdf', '.odt', '.rtf', '.xls', '.xlsx'):
                        new_jpg = f'{item["name"].replace(os.path.splitext(item["name"])[1], '')}.jpg'
                        filenames.append(new_jpg)
                        href = item['sizes'][9]['url']
                        await download_file(session, href, new_jpg)
                    else:
                        filenames.append(item['name'])
                        href = item['sizes'][0]['url']
                        await download_file(session, href, item['name'])
            return filenames
        else:
            print(f"Файлы не найдены")
            return None
async def send_schedule(filename, chat_id):
    # Первый параметр - текст на Inline кнопке. Второй параметр - ID группы. Функция отправляет уже скачанный jpg файл в указанный чат
    file_path = os.path.join(save_dir, filename)
    try:
        photo = FSInputFile(file_path)
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=f'{filename.replace(os.path.splitext(filename)[1], '')}'
        )
    except FileNotFoundError:
        print('Файл не найден')
        return None
# asyncio.run(get_file_names_with_apload()) - Пример


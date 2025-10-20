import asyncio
import dotenv
import os

from telegraph.aio import Telegraph

from bot_control.database import return_from, set_path
from bot_control.get_schedule import get_schedule, parse_schedule

dotenv.load_dotenv("../bot_settings/BOT_SETTINGS.env")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

th = Telegraph(access_token=ACCESS_TOKEN)


async def schedule_page(chat_id: int, modifier: str, course: int, group: str):
    path = return_from(modifier,chat_id)['path']
    schedule = get_schedule(modifier, course, group)
    schedule = parse_schedule(schedule)
    if not path:
        res = await th.create_page(title='Расписание',html_content=schedule)
    else:
        res = await th.edit_page(path=path,html_content=schedule, title="Расписание")
    set_path(modifier,chat_id,res['path'])
    return res['url']
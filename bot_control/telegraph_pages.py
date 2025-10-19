import asyncio
import dotenv
import os

from telegraph.aio import Telegraph

from bot_control.database import return_from, set_path
from bot_control.get_schedule import get_schedule, parse_schedule

dotenv.load_dotenv("../bot_settings/BOT_SETTINGS.env")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


async def on_start() -> bool | Telegraph:
    th = Telegraph(access_token=ACCESS_TOKEN)
    if not ACCESS_TOKEN:
        res = await th.create_account("Bot",
                                      author_name="ScheduleBot",
                                      author_url='/ScheduleBot',
                                      replace_token=True)
        with open('../bot_settings/BOT_SETTINGS.env', 'a') as file:
            file.write(f'ACCESS_TOKEN = "{res['access_token']}"')
        return False
    return th

async def schedule_page(chat_id: int, modifier: str, course: int, group: str):
    th = await on_start()
    if not th:
        th = Telegraph(access_token=ACCESS_TOKEN)
    path = return_from(modifier,chat_id)['path']
    schedule = get_schedule(modifier, course, group)
    schedule = parse_schedule(schedule)
    if not path:
        res = await th.create_page(title='Расписание',html_content=schedule)
    else:
        res = await th.edit_page(path=path,html_content=schedule, title="Расписание")
    set_path(modifier,chat_id,res['path'])
    return res['url']



async def main():
    await on_start()

if __name__=='__main__':
    asyncio.run(main())
import datetime as dt
import asyncio

import dotenv
import os

from aiogram import Bot

from bot_control.database import return_table, check_source, get_groups_info, stop_event
from bot_control.telegraph_pages import schedule_page

dotenv.load_dotenv("../bot_settings/BOT_SETTINGS.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)

class Restartable:
	def __init__(self,func):
		self.func=func
		self.task=asyncio.create_task(func())

	def start(self):
		return asyncio.create_task(self.func())

	def is_done(self):
		return

async def wait_notify(table: str) -> (str, int, int):
	now = dt.datetime.now().astimezone()
	# Убираем смещение UTC сервера и добавляем Перми
	perm_time = now - now.utcoffset() + dt.timedelta(hours=5)
	data: list[dict] =[]
	for row in return_table(table):
		if not row['enabled']:
			pass
		time = dt.datetime.strptime(row['time'],"%H:%M")
		time = time.replace(tzinfo=dt.timezone(dt.timedelta(hours=5)))
		#Если Tomorrow, прибавляем только 1 день, если Weekly, то до воскресенья
		time += dt.timedelta(days=table == "Tomorrow" +
		                          table == "Weekly" * (6 - now.weekday()))
		data.append({"sleep": abs((time - perm_time).total_seconds()),
		                   "chat_id": row['id']})
	sleep_list=[i['sleep'] for i in data]
	if not sleep_list:
		#Если нет уведомлений, за 300 дней точно появятся и перезапустят функцию
		await asyncio.sleep(dt.timedelta(days=300).total_seconds())
	sleep_time=min(sleep_list)
	index=sleep_list.index(sleep_time)
	_,chat_id = data[index].values()
	await asyncio.sleep(sleep_time)
	return chat_id

async def send_message(table: str) -> None:
	check_source(table,include_groups=False)
	chat_id = await wait_notify(table)
	_, group, course = get_groups_info(chat_id)
	url = schedule_page(chat_id=chat_id,
	                    modifier=table,
	                    course=int(course),
	                    group=group)
	await bot.send_message(chat_id=chat_id,
	                       text=f'[Пришло уведомление с расписанием!]({url})',
	                       parse_mode='Markdown')


async def notifications() -> None:
	async def weekly():
		await send_message("Weekly")

	async def today():
		await send_message("Today")

	async def tomorrow():
		await send_message("Tomorrow")

	weekly = Restartable(weekly)
	everyday = Restartable(today)
	tomorrow = Restartable(tomorrow)

	while True:
		await asyncio.sleep(5)
		if stop_event.is_set():
			weekly = await weekly.start()
			everyday = await everyday.start()
			tomorrow = await tomorrow.start()
			stop_event.clear()
		if weekly.is_done():
			weekly.start()
		if everyday.is_done():
			everyday.start()
		if tomorrow.is_done():
			tomorrow.start()
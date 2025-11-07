import datetime as dt
import asyncio

import os

from aiogram import Bot

from bot_control.database import return_table, check_source, get_groups_info, stop_event
from bot_control.telegraph_pages import schedule_page

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(BOT_TOKEN)

class Restartable:
	def __init__(self,func):
		self.func=func
		self.task=asyncio.create_task(func())

	def start(self):
		return asyncio.create_task(self.func())

	def is_done(self) -> bool:
		return self.task.done()

async def wait_notify(table: str) -> int | None:
	now : dt.datetime = dt.datetime.now().astimezone()
	# Убираем смещение UTC сервера и добавляем Перми
	perm_time : dt.datetime = now - now.utcoffset() + dt.timedelta(hours=5)
	data: list[ dict[str, str|int] ] = []
	for row in return_table(table):
		if not row['enabled']:
			continue
		time = dt.datetime.strptime(row['time'],"%H:%M")
		time = time.replace(tzinfo=dt.timezone(dt.timedelta(hours=5)))

		# Если Tomorrow, прибавляем только 1 день, если Weekly, то до воскресенья
		time += dt.timedelta(days=table == "Tomorrow" +
		                          table == "Weekly" * (6 - now.weekday()))
		data.append({"sleep": abs((time - perm_time).total_seconds()),
		             "chat_id": row['id']})
	sleep_list=[i['sleep'] for i in data]
	if not sleep_list:
		return None
	sleep_time=min(sleep_list)
	index=sleep_list.index(sleep_time)
	_,chat_id = data[index].values()
	await asyncio.sleep(sleep_time)
	return chat_id

async def _send_message(table: str) -> None:
	chat_id : int | None = await wait_notify(table)
	if chat_id is None:
		return
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
		await _send_message("Weekly")

	async def today():
		await _send_message("Today")

	async def tomorrow():
		await _send_message("Tomorrow")

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
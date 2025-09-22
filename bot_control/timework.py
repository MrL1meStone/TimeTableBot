import datetime
import asyncio
from aiogram import Bot
from datetime import datetime,time
from bot_control.database import return_table


async def weekly(bot: Bot) -> None:
	time_list = [time.fromisoformat(row['time']) for row in return_table("Weekly")]
	now = datetime.now()

	if now.time() not in time_list:
		sunday = now.replace(day=now.day + 6 - now.weekday())
		sleep_list=[(datetime.combine(sunday,time)-now).total_seconds() for time in time_list]
		print(f'sleep {min(sleep_list)}')
		await asyncio.sleep(min(sleep_list))

	for group in return_table("Weekly"):
		if group['time'] in time_list and bool(group['enabled']):
			await bot.send_message(chat_id=group['id'],text='123')

if __name__ !="__main__":
	print("Модуль импортирован")

# async def tomorrow()

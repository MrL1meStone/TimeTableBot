import datetime
import asyncio
from aiogram import Bot
from datetime import datetime,time
from bot_control.database import return_table, return_groups
from bot_control.get_schedule import get_schedule, parse_schedule
from bot_control.telegraph_pages import create_telegraph_page


async def weekly(bot: Bot) -> None:
	time_list = [time.fromisoformat(row['time']) for row in return_table("Weekly")]
	print(time_list)
	now = datetime.now()
	if now.time() not in time_list:
		sunday = now.replace(day=now.day + 6 - now.weekday())
		sleep_list=[(datetime.combine(sunday,time)-now).total_seconds() for time in time_list]
		print(min(sleep_list))
		await asyncio.sleep(abs(min(sleep_list)))
		print("Оконачание ожидания")

	for group in return_table("Weekly"):
		if datetime.strptime(group['time'], "%H:%M:%S").time() in time_list and bool(group['enabled']):
			group_id,groups_group,course=return_groups(group['id']).values()
			schedule = get_schedule(modifier="Weekly", course=int(course), group=groups_group)
			message = parse_schedule(schedule)
			res = await create_telegraph_page(title=f'Расписание на неделю для группы {groups_group}',
			                                  content_html=message)
			await bot.send_message(text=f'[Вот расписание на неделю:]({res['result']['url']})',
			                              parse_mode="Markdown",
			                       chat_id=group_id)


# async def tomorrow()

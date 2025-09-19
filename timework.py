import datetime
import asyncio

from database import return_from, return_table, check_source

NOW=datetime.datetime.now()

async def weekly() -> None:
	if NOW.date().day!="Sunday":
		await asyncio.sleep(60*60*24)
	elif NOW.time().hour not in [datetime.time(time).hour for time in return_table('Weekly')]:
		await asyncio.sleep(60*60)
	elif NOW.time().minute not in [datetime.time(time).minute for time in return_table('Weekly')]:
		await asyncio.sleep(60)
	else:
		[datetime.time(time) for time in return_table('Weekly')]
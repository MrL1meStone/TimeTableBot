import datetime
import asyncio

from database import return_from, return_table

NOW=datetime.datetime.now()

async def weekly() -> None:
	if NOW.date().day!="Sunday":
		await asyncio.sleep(60*60*24)
	if NOW.time().hour not in return_table('Weekly'):
		await asyncio.sleep(60*60)
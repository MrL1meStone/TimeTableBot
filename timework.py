import datetime
import asyncio

NOW=datetime.datetime.now()

async def weekly() -> None:
	if NOW.date().day!="Sunday":
		await asyncio.sleep(3600*24)

import datetime
import sqlite3
import asyncio

connection = sqlite3.connect('bot_settings/groups.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Groups (
id INTEGER PRIMARY KEY,
groups TEXT NOT NULL,
course TEXT NOT NULL) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Weekly (
id INTEGER PRIMARY KEY,
time TIME NOT NULL,
enabled BIT NOT NULL) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Tomorrow (
id INTEGER PRIMARY KEY,
time TIME NOT NULL,
enabled BIT NOT NULL) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Today (
id INTEGER PRIMARY KEY,
time TIME NOT NULL,
enabled BIT NOT NULL) ''')

stop_event = asyncio.Event()

def commit() -> None:
	connection.commit()
	print("Остановка тасков...")
	stop_event.set()

def check_source(source: str ,include_groups: bool = True) -> True:
	"""
	Checks the spelling of arguments for functions / Проверяет правильность написания аргументов функций
	:param include_groups: include 'Groups' to allowed list of values / Добавить 'Groups' в список разрешенных значений
	:param source: table of DB that need to check spell / Таблица БД написание которой надо проверить
	:return: True if spell is right else ValueError / True если все верно, иначе ValueError
	"""
	source_filter=("Groups","Weekly","Tomorrow","Today") if include_groups else ("Weekly","Tomorrow","Today")
	if source not in source_filter:
		raise ValueError(f"Некорректное название таблицы {source} для поиска")
	return True

def add_to(source: str , chat_id: int, time: str) -> None:
	"""
	Adds chat id to DB to use schedule notifications /Добавляет ID чата в телеграмме для дальнейшего использования
	:param source: table of DB where it's need to search /Таблица БД где нужно искать
	:param chat_id: ID of telegram chat where bot will send schedule /ID чата в телеграмме где бот будет публиковать расписание
	:param time: time when it's need to send schedule / Время когда надо присылать расписание
	:return: None
	"""
	check_source(source,include_groups=False)
	cursor.execute(f'INSERT INTO {source} (id, time, enabled) VALUES (?, ?, 1)', (chat_id,time))

def set_group(chat_id: int , group: str, course: str) -> None:
	"""
	Adds chat id to DB to use schedule notifications /Добавляет ID чата в телеграмме для дальнейшего использования
	:param chat_id: ID of telegram chat where bot will send schedule /ID чата в телеграмме где бот будет публиковать расписание
	:param group: group of college /Группа колледжа, для которой нужно искать расписание
	:return: None
	"""
	if not is_in("Groups",chat_id):
		for source in ("Weekly", "Tomorrow", "Today"):
			add_to(source, chat_id, "08:00:00")
		cursor.execute('INSERT INTO Groups (id,groups,course) VALUES (?, ?, ?)', (chat_id, group, course))
	else:
		cursor.execute('UPDATE Groups SET groups = ? WHERE id = ?', (group,chat_id))
	commit()

def is_in(source: str , chat_id: int) -> bool:
	"""
	Returns is chat ID in table of DB / Возвращает, есть ли ID чата в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search /Таблица БД где нужно искать
	:return: True if chat in table, else False / True если чат есть в БД, иначе False
	"""
	check_source(source)
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return bool(cursor.fetchone())

def get_groups_info(chat_id: int) -> dict[str,str]:
	if not is_in("Groups",chat_id):
		raise ValueError("Группы нет в БД")
	cursor.execute(f"SELECT groups,course FROM Groups WHERE id=?", (chat_id,))
	return dict(zip(("group", "course"), cursor.fetchone()))

def return_from(source: str,chat_id: int) -> dict:
	"""
	Returns time/group in table of DB / Возвращает группу/время из таблицы БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search / Таблица БД где нужно искать
	:return: data in table of DB / Данные в таблице БД
	"""
	check_source(source,include_groups=False)
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return dict(zip(("id","time","enabled"),cursor.fetchone()))

def return_table(source: str) -> list[dict]:
	"""
	Returns table of DB / Возвращает таблицу БД
	:param source: table of DB where it's need to return / Таблица БД которую нужно вернуть
	:return: table of DB / Таблица БД
	"""
	check_source(source)
	cursor.execute(f"SELECT * FROM {source}")
	return [dict(zip(("id","time","enabled"),row)) for row in cursor.fetchall()]

def remove_from(source: str, chat_id: int) -> None:
	"""
	Deletes data in table of DB/ Удаляет данные в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search / Таблица БД где нужно искать
	:return: None
	"""
	if not is_in(source,chat_id):
		raise ValueError(f"Указанного ID '{chat_id}' нет в таблице БД")
	check_source(source)
	cursor.execute(f'DELETE FROM {source} WHERE id = ?', (chat_id,))
	commit()

def is_enabled(source: str, chat_id: int) -> bool:
	if not is_in(source,chat_id):
		raise ValueError(f"Указанного ID '{chat_id}' нет в таблице БД")
	check_source(source, include_groups=False)
	return bool(return_from(source,chat_id)["enabled"])

def turn_notification(source: str, chat_id: int) -> None:
	enabled=int(not(is_enabled(source,chat_id)))
	cursor.execute(f'UPDATE {source} SET enabled = ? WHERE id = ?', (enabled,chat_id))
	commit()

def change_time(source: str, chat_id: int, time: datetime.time) -> None:
	check_source(source,include_groups=False)
	cursor.execute(f'UPDATE {source} SET time = ? WHERE id = ?', (str(time),chat_id))
	commit()

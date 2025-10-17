import sqlite3
import asyncio

connection = sqlite3.connect('bot_settings/groups.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Groups (
id INTEGER PRIMARY KEY,
groups TEXT NOT NULL,
course INTEGER NOT NULL) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Weekly (
id INTEGER PRIMARY KEY,
time TIME NOT NULL,
enabled BIT NOT NULL,
path TEXT) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Tomorrow (
id INTEGER PRIMARY KEY,
time TIME NOT NULL,
enabled BIT NOT NULL,
path TEXT) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Today (
id INTEGER PRIMARY KEY,
time TIME NOT NULL,
enabled BIT NOT NULL,
path TEXT) ''')

stop_event = asyncio.Event()

def commit() -> None:
	connection.commit()
	stop_event.set()

def check_source(source: str ,include_groups: bool = True) -> True:
	"""
	Проверяет правильность написания аргументов функций
	:param include_groups: Добавить 'Groups' в список разрешенных значений
	:param source: Таблица БД написание которой надо проверить
	:return: True если все верно, иначе ValueError
	"""
	source_filter=("Groups","Weekly","Tomorrow","Today") if include_groups else ("Weekly","Tomorrow","Today")
	if source not in source_filter:
		raise ValueError(f"Некорректное название таблицы {source} для поиска")
	return True

def add_to(source: str , chat_id: int, time: str) -> None:
	"""
	Добавляет ID чата в телеграмме для дальнейшего использования
	:param source: Таблица БД где нужно искать
	:param chat_id: ID чата в телеграмме, где бот будет публиковать расписание
	:param time: Время когда надо присылать расписание
	:return: None
	"""
	check_source(source,include_groups=False)
	cursor.execute(f'INSERT INTO {source} (id, time, enabled) VALUES (?, ?, 1)', (chat_id,time))

def set_group(chat_id: int , group: str, course: int) -> None:
	"""
	Добавляет ID чата в телеграмме для дальнейшего использования
	:param chat_id: ID чата в телеграмме, где бот будет публиковать расписание
	:param group: Группа колледжа, для которой нужно искать расписание
	:param course: Ваш курс в колледже
	:return: None
	"""
	if not is_in("Groups",chat_id):
		for table in ("Weekly", "Tomorrow", "Today"):
			add_to(table, chat_id, "08:00")
		cursor.execute('INSERT INTO Groups (id,groups,course) VALUES (?, ?, ?)', (chat_id, group, course))
	else:
		cursor.execute('UPDATE Groups SET groups = ?, course = ? WHERE id = ?', (group, course, chat_id))
	commit()

def is_in(source: str , chat_id: int) -> bool:
	"""
	Возвращает, есть ли ID чата в таблице БД
	:param chat_id: ID чата в телеграмме
	:param source: Таблица БД где нужно искать
	:return: True если чат есть в БД, иначе False
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
	Возвращает группу/время из таблицы БД
	:param chat_id: ID чата в телеграмме
	:param source: Таблица БД где нужно искать
	:return: Данные в таблице БД
	"""
	check_source(source,include_groups=False)
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return dict(zip(("id","time","enabled","path"),cursor.fetchone()))

def return_groups(chat_id: int) -> dict:
	cursor.execute(f"SELECT * FROM Groups WHERE id=?", (chat_id,))
	return dict(zip(("id", "group", "course"), cursor.fetchone()))

def return_table(source: str) -> list[dict]:
	"""
	Возвращает таблицу БД
	:param source: Таблица БД которую нужно вернуть
	:return: Таблица БД
	"""
	check_source(source,include_groups=False)
	cursor.execute(f"SELECT * FROM {source}")
	return [dict(zip(("id","time","enabled","path"),row)) for row in cursor.fetchall()]

def remove_from(source: str, chat_id: int) -> None:
	"""
	Удаляет данные в таблице БД
	:param chat_id: ID чата в телеграмме
	:param source: Таблица БД где нужно искать
	:return: None
	"""
	if not is_in(source,chat_id):
		raise ValueError(f"Указанного ID '{chat_id}' нет в таблице БД")
	check_source(source)
	cursor.execute(f'DELETE FROM {source} WHERE id = ?', (chat_id,))
	commit()

def is_enabled(source: str, chat_id: int) -> bool:
	"""
	Возвращает надо ли отправлять уведомления типа source
	:param source: Тип уведомления
	:param chat_id: ID чата в телеграмме
	:return:
	"""
	if not is_in(source,chat_id):
		raise ValueError(f"Указанного ID '{chat_id}' нет в таблице БД")
	check_source(source, include_groups=False)
	return bool(return_from(source,chat_id)["enabled"])

def turn_notification(source: str, chat_id: int) -> None:
	"""
	Изменяет разрешение отправки уведомлений в БД
	:param source: Тип уведомления
	:param chat_id: ID чата в телеграмме
	:return:
	"""
	enabled=int(not(is_enabled(source,chat_id)))
	cursor.execute(f'UPDATE {source} SET enabled = ? WHERE id = ?', (enabled,chat_id))
	commit()

def change_time(source: str, chat_id: int, time: str) -> None:
	"""
	Изменяет время отправки уведомления в БД
	:param source: Тип уведомления
	:param chat_id: ID чата в телеграмме
	:param time: Новое время
	:return:
	"""
	check_source(source,include_groups=False)
	cursor.execute(f'UPDATE {source} SET time = ? WHERE id = ?', (time,chat_id))
	commit()

def set_path(source: str, chat_id: int, path: str) -> None:
	"""
	Изменяет путь статьи для расписания
	:param source: Тип расписания
	:param chat_id: Айди чата в телеграмме
	:param path: Путь для статьи
	:return: None
	"""
	check_source(source, include_groups=False)
	cursor.execute(f'UPDATE {source} SET path = ? WHERE id = ?', (path, chat_id))
	commit()

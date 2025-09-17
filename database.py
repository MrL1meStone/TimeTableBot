import sqlite3

connection = sqlite3.connect('groups.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Groups (
id INTEGER PRIMARY KEY,
groups TEXT NOT NULL) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Weekly (
id INTEGER PRIMARY KEY,
time TIME) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Tomorrow (
id INTEGER PRIMARY KEY,
time TIME) ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Today (
id INTEGER PRIMARY KEY,
time TIME) ''')

def set_group(chat_id,group) -> None | int:
	"""
	Adds chat id to DB to use timetable notifications /Добавляет ID чата в телеграмме для дальнейшего использования
	:param chat_id: ID of telegram chat where bot will send timetable /ID чата в телеграмме где бот будет публиковать расписание
	:param group: group of college /Группа колледжа, для которой нужно искать расписание
	:return: None
	"""
	cursor.execute('INSERT INTO Groups (id,groups) VALUES (?, ?)'
	               'ON CONFLICT(id) DO UPDATE SET groups = excluded.groups', (chat_id,group))
	connection.commit()

def is_in(chat_id,source) -> bool:
	"""
	Returns is chat ID in table of DB / Возвращает, есть ли ID чата в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search /Таблица БД где нужно искать
	:return: True if chat in table, else False / True если чат есть в БД, иначе False
	"""
	if source not in ("Groups","Weekly","Tomorrow","Today"):
		raise ValueError(f"Некорректное название таблицы {source} для поиска")
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return bool(cursor.fetchone())

def search_in(chat_id, source) -> list:
	"""
	Returns list of data in table of DB/ Возвращает список данных в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search / Таблица БД где нужно искать
	:return: List of data in table of DB / Список данных в таблице БД
	"""
	if source not in ("Groups","Weekly","Tomorrow","Today"):
		raise ValueError(f"Некорректное название таблицы {source} для поиска")
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return cursor.fetchall()


def remove_from(chat_id,source) -> None:
	"""
	Deletes data in table of DB/ Удаляет данные в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search / Таблица БД где нужно искать
	:return: None
	"""
	if source not in ("Groups","Weekly","Tomorrow","Today"):
		raise ValueError(f"Некорректное название таблицы {source} для поиска")
	cursor.execute(f'DELETE FROM {source} WHERE id = ?', (chat_id,))
	connection.commit()


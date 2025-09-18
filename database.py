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

def check_source(source) -> True | ValueError:
	"""
	Checks the spelling of arguments for functions / Проверяет правильность написания аргументов функций
	:param source: table of DB that need to check spell / Таблица БД написание которой надо проверить
	:return: True if spell is right else ValueError / True если все верно, иначе ValueError
	"""
	if source not in ("Groups","Weekly","Tomorrow","Today"):
		raise ValueError(f"Некорректное название таблицы {source} для поиска")
	return True

def add_to(source, chat_id, time) -> None:
	"""
	Adds chat id to DB to use timetable notifications /Добавляет ID чата в телеграмме для дальнейшего использования
	:param source: table of DB where it's need to search /Таблица БД где нужно искать
	:param chat_id: ID of telegram chat where bot will send timetable /ID чата в телеграмме где бот будет публиковать расписание
	:param time: time when it's need to send timetable / Время когда надо присылать расписание
	:return: None
	"""
	check_source(source)
	cursor.execute(f'INSERT INTO {source} (id, time) VALUES (?, ?)', (chat_id,time))

def set_group(chat_id,group) -> None | int:
	"""
	Adds chat id to DB to use timetable notifications /Добавляет ID чата в телеграмме для дальнейшего использования
	:param chat_id: ID of telegram chat where bot will send timetable /ID чата в телеграмме где бот будет публиковать расписание
	:param group: group of college /Группа колледжа, для которой нужно искать расписание
	:return: None
	"""
	cursor.execute('INSERT INTO Groups (id,groups) VALUES (?, ?)'
	               'ON CONFLICT(id) DO UPDATE SET groups = excluded.groups', (chat_id,group))
	for source in ("Weekly","Tomorrow","Today"):
		add_to(source,chat_id,"08:00")
	connection.commit()

def is_in(chat_id,source) -> bool:
	"""
	Returns is chat ID in table of DB / Возвращает, есть ли ID чата в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search /Таблица БД где нужно искать
	:return: True if chat in table, else False / True если чат есть в БД, иначе False
	"""
	check_source(source)
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return bool(cursor.fetchone())

def return_from(chat_id, source) -> str:
	"""
	Returns time/group in table of DB / Возвращает группу/время из таблицы БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search / Таблица БД где нужно искать
	:return: data in table of DB / Данные в таблице БД
	"""
	check_source(source)
	cursor.execute(f"SELECT * FROM {source} WHERE id=?", (chat_id,))
	return cursor.fetchall()[0]

def return_table(source) -> list:
	"""
	Returns table of DB / Возвращает таблицу БД
	:param source: table of DB where it's need to return / Таблица БД которую нужно вернуть
	:return: table of DB / Таблица БД
	"""
	check_source(source)
	cursor.execute(f"SELECT * FROM {source}")
	return cursor.fetchall()

def remove_from(chat_id,source) -> None:
	"""
	Deletes data in table of DB/ Удаляет данные в таблице БД
	:param chat_id: ID of telegram chat / ID чата в телеграмм
	:param source: table of DB where it's need to search / Таблица БД где нужно искать
	:return: None
	"""
	check_source(source)
	cursor.execute(f'DELETE FROM {source} WHERE id = ?', (chat_id,))
	connection.commit()


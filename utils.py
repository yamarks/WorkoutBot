import datetime
import logging
import os

import pytz

import db


def create_user(user_id: int, username: str, fullname: str) -> None:
	"""Проверяет наличие игрока и добавляет его в базу, если игрока нет"""
	if not db.user_exists(user_id):
		db.add_user(user_id, username, fullname)


def create_database() -> None:
	# try to create .db file
	if not os.path.isfile("database.db"):
		file = open("database.db", "x")
		file.close()
	# try to connect to the database
	try:
		db.sqlite3.connect(db.db_name)
		db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()[0]
		logging.debug(f"Database '{db.db_name}' is ok.")
	except FileNotFoundError:
		logging.debug(f"Table 'users' was not found.")
		logging.debug(f"Creating...")
		db.cursor.execute("CREATE TABLE users")
		logging.debug(f"Created.")


def get_now_datetime() -> datetime.datetime:
	"""Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
	moscow_timezone = pytz.timezone("Europe/Moscow")
	moscow_time = datetime.datetime.now(moscow_timezone)
	return moscow_time

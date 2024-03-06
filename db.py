import math
import sqlite3

from utils import get_now_datetime

db_name = "database.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()


def user_exists(user_id: int) -> bool:
    """Checks if user exists in database"""
    result = cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    return bool(len(result.fetchall()))


def add_user(user_id: int, username: str, profile_name: str) -> None:
    """Добавляем пользователя в базу"""
    cursor.execute(
        "INSERT INTO users (user_id, username, profilename) VALUES (?, ?, ?)", (user_id, username, profile_name)
    )
    return conn.commit()


def user_pullups(user_id: int, pullups: int) -> None:
    """Изменяет результат пользователя"""
    cursor.execute("UPDATE users SET pulls_count = ? WHERE user_id = ?", (pullups, user_id))
    return conn.commit()


def get_max(user_id: int) -> int:
    """Возвращает цель, заданную пользователем"""
    curr_max = cursor.execute("SELECT user_max FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    return int(curr_max)


def get_user_stats(user_id: int):
    user_max = cursor.execute("SELECT user_max FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    half_max = cursor.execute("SELECT half_max FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    third = cursor.execute("SELECT third FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    fourth = cursor.execute("SELECT fourth FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    fifth = cursor.execute("SELECT fifth FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    return int(user_max), int(half_max), int(third), int(fourth), int(fifth)


def update_max(user_id: int, user_max: int):
    current_max = int(cursor.execute("SELECT user_max FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])
    if current_max == 0:
        current_max = user_max
        cursor.execute("UPDATE users SET user_max = ?", (current_max,))
    elif current_max == user_max:
        current_max += 1
        cursor.execute("UPDATE users SET user_max = ?", (current_max,))
    elif current_max > user_max:
        current_max -= 1
        cursor.execute("UPDATE users SET user_max = ?", (current_max,))
    return conn.commit()


def increase_max(user_id: int):
    current_max = int(cursor.execute("SELECT user_max FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])
    current_max += 1
    cursor.execute("UPDATE users SET user_max = ? WHERE user_id = ?", (current_max, user_id))
    conn.commit()
    return update_user_stats(user_id)


def set_max(user_id: int, user_max: int):
    cursor.execute("UPDATE users SET user_max = ? WHERE user_id = ?", (user_max, user_id))
    return conn.commit()

def update_user_stats(user_id: int):
    new_max = int(cursor.execute("SELECT user_max FROM users WHERE user_id = ?", (user_id,)).fetchone()[0])
    half_max = math.ceil(new_max / 2)
    third, fourth, fifth = half_max - 2, half_max - 3, half_max - 4
    cursor.execute("UPDATE users SET user_max = ?, half_max = ?, third = ?, fourth = ?, fifth = ? WHERE user_id = ?", (new_max, half_max, third, fourth, fifth, user_id))
    return conn.commit()

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

goal = KeyboardButton(text="Задать цель")
pullups = KeyboardButton(text="Записать результат")
cancel = KeyboardButton(text="Отмена")

kb_default = ReplyKeyboardMarkup(resize_keyboard=True)
kb_default.add(goal, pullups).add(cancel)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel.add(cancel)

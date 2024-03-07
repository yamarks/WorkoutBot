import logging
import math
import os
import asyncio

import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

import db
import keyboards
import utils
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

tasks = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class UserChoice(StatesGroup):
    user_max = State()
    pullups = State()


async def on_startup(_) -> None:
    print("All systems nominal.")


@dp.message_handler(commands=["start", "старт", "начать"])
async def start_command(message: types.Message) -> None:
    utils.create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.reply(
        f"Приветствую, воин! Чтобы задать текущую цель, используй /goal. Чтобы записать прогресс, используй /pullups.",
        reply_markup=keyboards.kb_default
    )


@dp.message_handler(regexp="^Отмена$|/cancel", state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Ладно, забыли.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(regexp="^Задать цель$|/max")
async def max_command(message: types.Message) -> None:
    await message.answer("Воин, сколько раз можешь подтянуться?")
    await UserChoice.user_max.set()


# Check goal. Gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=UserChoice.user_max)
async def process_max_invalid(message: types.Message):
    """
    If user_max is invalid
    """
    return await message.reply("Воин, укажи свой максимум в виде числа.")


@dp.message_handler(lambda message: message.text.isdigit(), state=UserChoice.user_max)
async def process_max(message: types.Message, state: FSMContext):
    # Update state and data
    await state.update_data(goal=int(message.text))
    user_input = int(message.text)
    user_id = message.from_user.id

    if user_input > 100:
        return await message.answer("Воин, тебе стоит подтягиваться с дополнительным весом!")

    user_max = user_input
    half_max = math.ceil(user_max / 2)
    third = half_max - 2
    fourth = half_max - 3
    fifth = half_max - 4
    db.set_max(user_id, user_max)
    db.update_user_stats(user_id)
    await state.finish()
    if user_max <= 10:
        await message.reply(f"Сделай 2 подхода: {user_max} + {half_max + 1}")
    else:
        await message.reply(
            f"Сделай 5 подходов: {user_max} + {half_max} + {third} + {fourth} + {fifth}")


@dp.message_handler(regexp="^Записать результат$|/pullups")
async def pullups_command(message: types.Message) -> None:
    await message.answer(text="Сколько раз подтянулся сегодня?", reply_markup=keyboards.kb_cancel)
    await UserChoice.pullups.set()


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserChoice.pullups)
async def process_pullups_invalid(message: types.Message):
    """
    If pullups is invalid
    """
    return await message.reply("Воин, вводи только число.")


@dp.message_handler(lambda message: message.text.isdigit(), state=UserChoice.pullups)
async def process_pullups(message: types.Message, state: FSMContext):
    # Update state and data
    await state.update_data(pullups=int(message.text))
    await state.finish()

    user_pullups = int(message.text)
    user_max = db.get_max(message.from_user.id)
    if user_pullups < user_max:
        await message.reply("Воин, ты не достиг цели. В следующий раз старайся усерднее.")
        db.update_max(user_id=message.from_user.id, user_max=user_pullups)
    elif user_pullups == user_max:
        await message.reply("Молодец. Ты достиг цели. Теперь стремись выше.")
        db.update_max(user_id=message.from_user.id, user_max=user_max)
    else:
        await message.reply("Воин, ты оказался сильнее, чем ты думал. Будь увереннее в себе.")
    await send_message_12_hours_later(message)


async def send_message_12_hours_later(message: types.Message):
    user_id = message.from_user.id
    # Interval between new tasks in seconds
    seconds = os.getenv("INTERVAL")
    await asyncio.sleep(int(seconds))
    user_max, half_max, third, fourth, fifth = db.get_user_stats(message.from_user.id)
    user_max += 1
    try:
        await bot.send_message(
            user_id,
            text=f"Привет, боец!\nТвоя программа на сегодня: {user_max} + {half_max} + {third} + {fourth} + {fifth}\n\nЕсли ты готов сдаться, просто заблокируй меня."
        )
        db.increase_max(user_id)
        await asyncio.create_task(send_message_12_hours_later(message))
        await send_message_12_hours_later(message)
    except aiogram.utils.exceptions.BotBlocked as err:
        print(f"{user_id}: blocked bot")


if __name__ == "__main__":
    utils.create_database()
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)

#dev

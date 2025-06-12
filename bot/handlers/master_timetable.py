from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.database.connection import get_pool
from bot.constants import BTN_MASTER_TIME
from bot.bot_utils import MasterTimetableStates
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from aiogram.filters import StateFilter


router = Router()

# Хендлер реакции на кнопку мастера Розклад
@router.message(F.text == BTN_MASTER_TIME)
async def master_timetable_handler(message: Message, state: FSMContext):
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow('''
                                      SELECT start_work_time, end_work_time
                                      FROM masters
                                      ''')
        await state.set_state(MasterTimetableStates.waiting_for_schedule)
        await message.answer(f"Зараз ти працюєш з {row['start_work_time'].strftime(('%H:%M'))} до {row['end_work_time'].strftime(('%H:%M'))}\n\nЯкщо хочеш змінити час роботи, то в полі повідомлення введи новий час початку та час закінчення роботи через пробіл. Наприклад, 9:00 14:00")
    except Exception as e:
        print(f"[master_timatable_handler] Error: {e}")
        await message.answer("🚨 Сталась помилка при надсиланні повідомлення.")

# Хендлер смены времени работы мастера
@router.message(F.text, StateFilter(MasterTimetableStates.waiting_for_schedule))
async def receive_review_text(message: Message, state: FSMContext):
    try:
        receive_text = message.text
        start_str, end_str = receive_text.split(" ")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        print(start, end)
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                               UPDATE masters
                               SET start_work_time = $1, end_work_time = $2
                               ''', start, end)
        await message.answer(f"Тепер ти працюєш з {start} до {end}")
    except Exception as e:
        print(f"[master_timatable_handler_text] Error: {e}")
        await message.answer("🚨 Сталась помилка при записі в базу даних.")
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.database.connection import get_pool
from bot.constants import BTN_MASTER_TIME
from bot.bot_utils import MasterTimetableStates
from aiogram.filters import StateFilter
from datetime import datetime

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

        # Инлайновая клавиатура
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Змінити розклад", callback_data="change_schedule")],
                [InlineKeyboardButton(text="❌ Відмінити", callback_data="cancel_schedule")]
            ]
        )

        await message.answer(
            f"Зараз ти працюєш з {row['start_work_time'].strftime('%H:%M')} до {row['end_work_time'].strftime('%H:%M')}\n\n"
            "Якщо хочеш змінити час роботи — натисни кнопку нижче 👇",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"[master_timetable_handler] Error: {e}")
        await message.answer("🚨 Сталась помилка при надсиланні повідомлення.")

# Хендлер на "Змінити розклад" → ждем сообщение с временем
@router.callback_query(F.data == "change_schedule")
async def change_schedule_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterTimetableStates.waiting_for_schedule)
    await callback.message.answer(
        "Введи новий час початку та закінчення через пробіл. Наприклад: 9:00 14:00"
    )
    await callback.answer()

# Хендлер на "Відмінити" → сбрасываем state
@router.callback_query(F.data == "cancel_schedule")
async def cancel_schedule_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Окей, зміни розкладу скасовані.")
    await callback.answer()

# Хендлер смены времени работы мастера (по тексту)
@router.message(F.text, StateFilter(MasterTimetableStates.waiting_for_schedule))
async def receive_review_text(message: Message, state: FSMContext):
    try:
        receive_text = message.text
        start_str, end_str = receive_text.split(" ")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()

        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                               UPDATE masters
                               SET start_work_time = $1, end_work_time = $2
                               ''', start, end)

        await message.answer(f"✅ Тепер ти працюєш з {start.strftime('%H:%M')} до {end.strftime('%H:%M')}")
        await state.clear()  # Обязательно сбрасываем state после успешного обновления

    except Exception as e:
        print(f"[master_timatable_handler_text] Error: {e}")
        await message.answer("🚨 Сталась помилка при записі в базу даних.")

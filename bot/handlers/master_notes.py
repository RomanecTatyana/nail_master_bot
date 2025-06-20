from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.database.connection import get_pool
from bot.constants import BTN_NOTES
from bot.bot_utils import MasterTimetableStates1
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from aiogram.filters import StateFilter

router = Router()

# Хендлер реакции на кнопку мастера Примітки
@router.message(F.text == BTN_NOTES)
async def master_notes_hendler(message: Message, state: FSMContext):
    try:
        stat = "done"
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('''SELECT DISTINCT ON (c.id) 
                                        c.id, 
                                        c.full_name,
                                        a.appointment_date,
                                        a.end_time
                                        FROM clients c
                                        JOIN appointments a ON c.id = a.client_id
                                        WHERE a.stat = $1
                                        ORDER BY c.id, a.appointment_date DESC, a.end_time DESC
                                        LIMIT 10''', stat)
        keyboard = []
        for row in rows:
            btn_text = row['full_name']
            callback_data = f"client_name;{row['id']}"
            keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
            inline_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(f"Обери клієнта, про якого хочеш залишити собі помітку", reply_markup=inline_markup)
    except Exception as e:
        print(f"[master_notes_handler] Error: {e}")
        await message.answer("🚨 Сталась помилка при надсиланні повідомлення.")  
        
#Запись в базу пометок о клиенте
@router.callback_query(F.data.startswith("client_name"))
async def master_notes(callback: CallbackQuery, state: FSMContext):
    try:
        _, id_str = callback.data.split(";")
        id = int(id_str)
        await state.update_data(id=id)
        await state.set_state(MasterTimetableStates1.waiting_for_client_note)
        await callback.message.answer(
            "✍️ Напиши, будь ласка, помітку про клієнта. Коли закінчиш — я її збережу в базу."
        )
        review_text = callback.message.text
        print(review_text)
    except Exception as e:
        print(f"[master_notes] Error: {e}")
        await callback.message.answer("Сталася помилка запису даних в базу")    
    
    @router.message(F.text, StateFilter(MasterTimetableStates1.waiting_for_client_note))
    async def receive_client_note(message: Message, state: FSMContext):
        try:
            data = await state.get_data()
            client_id = data.get("id")
            master_id = 1  # пока вручную, потом можно подставить реального мастера
            note_text = message.text
            now = datetime.now()

            pool = get_pool()
            async with pool.acquire() as conn:
                await conn.execute('''
                INSERT INTO client_notes (client_id, master_id, note, created_at)
                VALUES ($1, $2, $3, $4)
            ''', client_id, master_id, note_text, now)

            await message.answer("✅ Помітку збережено! Дякую 🙏")
        
        except Exception as e:
            print(f"[receive_client_note] Error: {e}")
            await message.answer("🚨 Сталася помилка при збереженні помітки.")
        # Чистим state, чтобы больше не ловить текст
        await state.clear()
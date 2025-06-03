from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.filters import Command
from ..constants import BTN_APPOINT
from bot.keyboards.menu import build_services_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.connection import get_pool
from aiogram.fsm.context import FSMContext
from urllib.parse import quote
from urllib.parse import urlencode
router = Router()

#Хендлер для показа всех актуальных записей клиента
@router.message(Command("appoints"))
async def appoints_hendler(message: Message):
    try:
        telegram_id = message.from_user.id
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                                    SELECT a.id, a.client_id, a.service_id, a.appointment_date, a.start_time,
                                           s.service_name
                                    FROM appointments a
                                    JOIN services s ON a.service_id=s.id
                                    WHERE a.client_id = (SELECT id FROM clients WHERE telegram_id = $1)
                                        AND a.stat = $2
                                    ORDER BY a.appointment_date, a.start_time
                                    ''', telegram_id, "active")
            if not rows:
                await message.answer("😔 Нажаль, Ваших записів не знайдено.")
                return
            
            response = "💅 <b>Ваші записи:</b>\n\n"
            appointments = []
            i = 1
            for row in rows:
                response += f"{i}. <b><u>{row['appointment_date']} о {row['start_time']}</u></b>\n    {row['service_name']}\n\n"
                i += 1
            await message.answer(response, parse_mode="HTML")    
            
    except Exception as e:
        await message.answer("🚨 Помилка при отриманні списку записів.")
        print(f"[appoints_hendler] Error: {e}")    

#Хендлер на кнопку с текстом актуальных записей
@router.message(F.text == BTN_APPOINT)
async def appoint_button_handler(message: Message):
    await appoints_hendler(message)
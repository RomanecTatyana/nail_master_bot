# bot/handlers/start.py

from aiogram import Router, types, F
from aiogram.filters import Command
from bot.database.connection import get_pool
import bot.keyboards.menu as menu

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    phone = None  # в будущем можно получать через WebApp

    pool = get_pool()

    async with pool.acquire() as conn:
        is_master = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM masters WHERE telegram_id = $1)",
            telegram_id)
        client = await conn.fetchrow("SELECT id FROM clients WHERE telegram_id = $1", telegram_id)

        if client is None:
            await conn.execute(
                "INSERT INTO clients (telegram_id, full_name, phone) VALUES ($1, $2, $3)",
                telegram_id, full_name, phone
            )
            await message.answer("Вітаємо! Ваш профіль створено.", reply_markup=menu.main_menu_with_cancel)
        elif is_master:
            await message.answer("👩‍🎨 Вітаю, майстре!", reply_markup=menu.master_main_menu)
        else:
            await message.answer(f"З поверненням, {full_name}!", reply_markup=menu.main_menu_with_cancel)

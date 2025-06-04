from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import asyncpg
import os
from dotenv import load_dotenv
from ..constants import BTN_REVIEWS
from aiogram import  F
from bot.database.connection import get_pool

load_dotenv()
router = Router()

def render_stars(rating: int, max_stars: int = 5) -> str:
    filled_star = "⭐"   # заполненная звезда
    empty_star = "☆"    # пустая звезда
    return filled_star * rating + empty_star * (max_stars - rating)

# Хендлер для /reviewes
@router.message(Command("reviewes"))
async def reviewes_handler(message: Message):
    try:
        pool = get_pool()
        async with pool.acquire() as conn:

            rows = await conn.fetch("SELECT full_name, comment, rating, DATE(created_at) AS created_date FROM reviews JOIN clients ON reviews.client_id = clients.id")
       

            if not rows:
                await message.answer("😔 Відгуки з'являться згодом.")
                return

            response = "ℹ️ <b>Відгуки:</b>\n\n"
            for row in rows:
                    response += f"{row['created_date']}\n"
                    response += f"<b>{row['full_name']}</b>\n"
    
                    comment = row['comment']
                    if comment:  # если комментарий не пустой или не None
                        response += f"{comment}\n"

                    response += f"{render_stars(row['rating'])}\n\n"

            await message.answer(response, parse_mode="HTML")
    except Exception as e:
        await message.answer("🚨 Помилка при отриманні списку послуг.")
        print(f"[reviewes_handler] Error: {e}")
        
# Хендлер на текст кнопки
@router.message(F.text==BTN_REVIEWS)
async def reviewes_button_handler(message: Message):
    await reviewes_handler(message)

from aiogram import Bot, Dispatcher, types, html, Router, F
from aiogram.types import Message
from dotenv import load_dotenv
import os
import asyncio
from aiogram.filters import Command
from pytz import timezone
import bot.keyboards.menu as menu
from bot.handlers import services, reviewes, start, appoints
from bot.database.connection import create_pool

load_dotenv()

router = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@router.message()
async def fallback_handler(message: Message):
    await message.answer(
        "Я Бот і не вмію відповідати на текстові повідомлення. Ось головне меню 👇",
        reply_markup=menu.main_menu_with_cancel
    )
    
    
async def main():
    await  create_pool()
    dp.include_router(services.router)
    dp.include_router(reviewes.router)
    dp.include_router(start.router)
    dp.include_router(appoints.router)
    dp.include_router(router) 
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())

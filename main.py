from aiogram import Bot, Dispatcher, types, html, Router, F
from aiogram.types import Message
from dotenv import load_dotenv
import os
import asyncio
from aiogram.filters import Command
from pytz import timezone
import bot.keyboards.menu as menu
from bot.handlers import services, reviewes, start, appoints, single_reviewes, master_appoint, master_timetable, master_notes
from bot.database.connection import get_pool, create_pool
import asyncio

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
    
async def update_appointments_job():
    while True:
        print("🔄 Запуск оновлення записів...")
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                UPDATE appointments
                SET stat = 'done'
                WHERE stat = 'active'
                  AND (appointment_date < CURRENT_DATE
                       OR (appointment_date = CURRENT_DATE AND end_time < CURRENT_TIME))
            ''')
            print("✅ Оновлення завершено.")
        
        await asyncio.sleep(43200)  # 12 часов в секундах (12 * 60 * 60)
        
            
async def main():
    await  create_pool()
    asyncio.create_task(update_appointments_job())
    dp.include_router(master_appoint.router)
    dp.include_router(master_timetable.router)
    dp.include_router(master_notes.router)
    dp.include_router(services.router)
    dp.include_router(reviewes.router)
    dp.include_router(start.router)
    dp.include_router(appoints.router)
    dp.include_router(single_reviewes.router)
    dp.include_router(router) 
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from dotenv import load_dotenv
import os
import asyncio
from aiogram.filters import Command
from pytz import timezone

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привіт! Це бот запису на манікюр 💅")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())

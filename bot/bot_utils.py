# bot_utils.py
import os
from aiogram import Bot
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

async def send_message_to_user(chat_id: int, service_name: str, time_str: str, date_str: str):
    text = f"Ви записані на {service_name} о {time_str} {date_str}"
    await bot.send_message(chat_id=chat_id, text=text)

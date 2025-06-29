# bot_utils.py
import os
from aiogram import Bot
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)



async def send_message_to_user(chat_id, service_name, time, date):
    bot = Bot(token=BOT_TOKEN)
    text = f"Ви записані на {service_name} о {time} {date}"
    await bot.send_message(chat_id, text)
    await bot.session.close()


from aiogram.fsm.state import StatesGroup, State

class MasterTimetableStates(StatesGroup):
    waiting_for_schedule = State()

class MasterTimetableStates1(StatesGroup):
    waiting_for_client_note = State()
    
class MasterBlockedTime(StatesGroup):
    waiting_for_blocked_time = State()
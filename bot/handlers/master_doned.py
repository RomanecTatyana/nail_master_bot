from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.database.connection import get_pool
from bot.constants import BTN_MASTER_APPOINT
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

router = Router()


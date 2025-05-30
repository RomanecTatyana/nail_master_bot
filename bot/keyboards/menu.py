from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..constants import BTN_SERVICES,BTN_REVIEWS
from aiogram import  F
from math import ceil

# Создаём кнопки главной клавиатуры
services_button = KeyboardButton(text=BTN_SERVICES)
reviews_button = KeyboardButton(text=BTN_REVIEWS)

# Клавиатура главная с двумя кнопками
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [services_button, reviews_button]
    ],
    resize_keyboard=True,  # делает кнопки меньше по высоте
    one_time_keyboard=False  # не скрывается после нажатия
)

# Создаем динамическую клавиатуру с названием услуг
def build_services_keyboard(services: list[str])->ReplyKeyboardMarkup:
    rows = [services[i:i+2] for i in range(0, len(services), 2)]
    keyboard = [[KeyboardButton(text=service) for service in row] for row in rows]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..constants import BTN_SERVICES,BTN_REVIEWS, BTN_REV, BTN_APPOINT, BTN_MASTER_APPOINT, BTN_DONE, BTN_MASTER_NO_WORK, BTN_MASTER_TIME, BTN_NOTES, BTN_REPORT, BTN_MASTER_HAND
from aiogram import  F
from math import ceil

# Создаём кнопки главной клавиатуры
services_button = KeyboardButton(text=BTN_SERVICES)
reviews_button = KeyboardButton(text=BTN_REVIEWS)
appoint_button = KeyboardButton(text=BTN_APPOINT)
rev_button = KeyboardButton(text=BTN_REV)

#Кнопки клавиатуры мастера маникюра
mas_appoint_button = KeyboardButton(text=BTN_MASTER_APPOINT)
mas_done_button = KeyboardButton(text=BTN_DONE)
mas_notes_button = KeyboardButton(text=BTN_NOTES)
mas_time_button = KeyboardButton(text=BTN_MASTER_TIME)
mas_report_button = KeyboardButton(text=BTN_REPORT)
mas_nowork_button = KeyboardButton(text=BTN_MASTER_NO_WORK)
mas_hand_button = KeyboardButton(text=BTN_MASTER_HAND)

# Клавиатура мастера маникюра
master_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [mas_hand_button],
        [mas_appoint_button, mas_notes_button],
        [reviews_button, mas_time_button],
        [mas_nowork_button]
    ],
    resize_keyboard=True,  # делает кнопки меньше по высоте
    one_time_keyboard=False  # не скрывается после нажатия
)

# Клавиатура главная с тремя кнопками
main_menu_with_cancel = ReplyKeyboardMarkup(
    keyboard=[
        [services_button, appoint_button],
        [reviews_button, rev_button]
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



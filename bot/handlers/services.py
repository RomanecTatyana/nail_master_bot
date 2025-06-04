from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.filters import Command
from bot.constants import BTN_SERVICES
from bot.keyboards.menu import build_services_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.connection import get_pool
from aiogram.fsm.context import FSMContext
from urllib.parse import quote
from urllib.parse import urlencode
router = Router()

# Хендлер для команды /services — показывает список услуг
@router.message(Command("services"))
async def services_handler(message: Message):
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, service_name, duration_minutes FROM services")

            if not rows:
                await message.answer("😔 Послуги ще не додані.")
                return

            response = "💅 <b>Доступні послуги:</b>\n\n"
            service_names = []
            for row in rows:
                response += f"• {row['service_name']} — {row['duration_minutes']} хв\n"
                service_names.append(row['service_name'])

            response += "\nОберіть послугу нижче 👇"

            # Генерация клавиатуры
            builder = InlineKeyboardBuilder()
            for row in rows:
                builder.button(
                    text=row['service_name'],
                    callback_data=f"choose_service:{row['id']}:{row['service_name']}:{row['duration_minutes']}",
                )
            builder.adjust(2)  # по 2 кнопки в ряд

            await message.answer(response, reply_markup=builder.as_markup(), parse_mode="HTML")

    except Exception as e:
        await message.answer("🚨 Помилка при отриманні списку послуг.")
        print(f"[services_handler] Error: {e}")

# Хендлер на кнопку с текстом услуг
@router.message(F.text == BTN_SERVICES)
async def services_button_handler(message: Message):
    await services_handler(message)

# Обработка выбора услуги из inline-кнопок
@router.callback_query(F.data.startswith("choose_service:"))
async def choose_service_handler(callback: CallbackQuery, state: FSMContext):
    try:
        _, service_id, service_name, service_duration = callback.data.split(":")
        # 1. Получаем telegram_id пользователя
        telegram_id = callback.from_user.id
        chat_id = callback.message.chat.id
        print (telegram_id, chat_id)
               # 2. Ищем клиента в базе
        pool = get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT id FROM clients WHERE telegram_id = $1", telegram_id)
        
        if not row:
            await callback.message.answer("Клієнт не знайдений у базі даних.")
            return

        client_id = row["id"]  # 3. Внутренний ID

        # 4. Сохраняем в состояние
        await state.update_data(
            service_id=service_id,
            service_name=service_name,
            service_duration=service_duration,
            client_id=client_id,
            chat_id=telegram_id
        )
        params = {
            "duration_minutes": service_duration,
            "service_id": service_id,
            "client_id": client_id,
            "chat_id": chat_id
        }
        # 5. Формируем WebApp URL
        web_app_url = (f"https://1fb1-46-63-12-99.ngrok-free.app?{urlencode(params)}")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text="🗓 Вибрати дату",
            web_app=WebAppInfo(url=web_app_url)
        )]])

        await callback.message.answer(
            f"Ви обрали послугу {service_name}. Тепер, будь ласка, оберіть дату у вікні нижче 👇",
            reply_markup=keyboard
        )
        
    except Exception as e:
        print(f"[choose_service_handler] Error: {e}")
        await callback.message.answer("Сталася помилка при обробці вибраної послуги.")


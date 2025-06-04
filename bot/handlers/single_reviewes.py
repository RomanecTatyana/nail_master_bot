from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.database.connection import get_pool
from bot.constants import BTN_REV
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
router = Router()

@router.message(F.text == BTN_REV)
async def leave_review_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT a.id, a.appointment_date, a.start_time, s.service_name
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                JOIN clients c ON a.client_id = c.id
                LEFT JOIN reviews r ON a.id = r.appointment_id
                WHERE c.telegram_id = $1 AND a.stat = 'done' AND r.appointment_id IS NULL
            ''', telegram_id)

            if not rows:
                await message.answer("😔 Ви ще не завершили жодної послуги, щоб залишити відгук.\n\n😉 Або Ви вже встигли мене оцінити раніше")
                return

            keyboard = []
            for row in rows:
                btn_text = f"{row['service_name']} - {row['appointment_date']} {row['start_time'].strftime('%H:%M')}"
                callback_data = f"review:{row['id']}"
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])

            await message.answer(
                "🙏 Дякую, що хочете залишити відгук!\n\n Оберіть отриману послугу нижче 👇",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
    except Exception as e:
        print(f"[leave_review_handler] Error: {e}")
        await message.answer("🚨 Сталась помилка при отриманні записів для відгуку.")

def build_rating_keyboard(selected=0):
            builder = InlineKeyboardBuilder()
            for i in range(1, 6):
                star = "⭐" if i <= selected else "☆"
                builder.button(text=star, callback_data=f"rate_review:{i}")
            builder.adjust(5)  # 5 кнопок в ряд
            return builder.as_markup()
        
@router.callback_query(F.data.startswith("review:"))
async def choose_review(callback: CallbackQuery, state: FSMContext):
    try:
        _, id_str = callback.data.split(":")
        id = int(id_str)
        telegram_id = callback.from_user.id
        await state.update_data(app_id = id)
        keyboard = build_rating_keyboard()
        await callback.message.answer(f"⭐ Оцініть послугу від 1 до 5 👇", reply_markup=keyboard)
    except Exception as e:
        print(f"[leave_review_handler] Error: {e}")
        await callback.message.answer("🚨 Сталась помилка при отриманні записів для відгуку.")
        
#Красим звезды        
@router.callback_query(F.data.startswith("rate_review:"))
async def handle_star_rating(callback: CallbackQuery, state: FSMContext):
    try:
        rating = int(callback.data.split(":")[1])
        await state.update_data(rating=rating)

        # Перерисовываем звезды с подсветкой
        new_kb = build_rating_keyboard(selected=rating)
        await callback.message.edit_reply_markup(reply_markup=new_kb)

        await callback.answer(f"Оцінка: {rating} ⭐")

        # Можем отправить следующее сообщение:
        await callback.message.answer(
            "✍️ Напишіть, будь ласка, декілька слів про Ваш досвід або натисніть «Пропустити».",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Пропустити", callback_data="skip_review")]]
            )
        )
    except Exception as e:
        print(f"[handle_star_rating] Error: {e}")

@router.callback_query(F.data == "skip_review")
async def handle_skip_review(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rating = data.get("rating")
    if not rating:
        await callback.message.answer("🚫 Оцінку не знайдено. Спробуйте ще раз.")
        return
    app_id = data.get("app_id")
    if not app_id:
        await callback.message.answer("🚫 Не знайдено запис для збереження відгуку.")
        return
    now = datetime.now()
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('''
                         SELECT client_id, master_id
                         FROM appointments
                         WHERE id = $1
                         ''', app_id)
        client_id = row["client_id"]
        master_id = row["master_id"]
        await conn.execute('''
                           INSERT INTO reviews (client_id, master_id, appointment_id, rating, created_at)
                           VALUES ($1, $2, $3, $4, $5)
            
        ''', client_id, master_id, app_id, rating, now)

    await callback.message.answer("✅ Дякуємо за оцінку!")
    await state.clear()

@router.message(F.text)
async def receive_review_text(message: Message, state: FSMContext):
    data = await state.get_data()
    rating = data.get("rating")
    app_id = data.get("app_id")

    if not rating or not app_id:
        return  # Сообщение не из процесса отзыва — игнорируем

    review_text = message.text

    now = datetime.now()
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('''
                         SELECT client_id, master_id
                         FROM appointments
                         WHERE id = $1
                         ''', app_id)
        client_id = row["client_id"]
        master_id = row["master_id"]
        await conn.execute('''
                           INSERT INTO reviews (client_id, master_id, appointment_id, rating, comment, created_at)
                           VALUES ($1, $2, $3, $4, $5, $6)
            
        ''', client_id, master_id, app_id, rating, review_text, now)

    await message.answer("✨ Дякуємо за Ваш відгук!")
    await state.clear()
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.connection import get_pool
from bot.constants import BTN_MASTER_NO_WORK
from bot.bot_utils import MasterBlockedTime
from aiogram.filters import StateFilter
from datetime import datetime
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# 1️⃣ Хендлер — реагируем на кнопку, устанавливаем состояние
@router.message(F.text == BTN_MASTER_NO_WORK)
async def master_no_work_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(MasterBlockedTime.waiting_for_blocked_time)
        
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_blocked_time")]
        ])
        
        await message.answer(
            "Введи дату, час початку, час закінчення та причину через ;\n\n"
            "Наприклад:\n2025-07-02;10:30;13:00;Не хочу працювати",
            reply_markup=inline_kb
        )
    except Exception as e:
        print(f"[master_no_work_handler] Error: {e}")
        await message.answer("🚨 Сталась помилка при надсиланні повідомлення.")

@router.callback_query(F.data == "cancel_blocked_time")
async def cancel_blocked_time(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Блокування скасовано. Можеш повернутися до меню.")

# 2️⃣ Хендлер — ловим текст с установленным состоянием
@router.message(StateFilter(MasterBlockedTime.waiting_for_blocked_time))
async def master_receive_blocked_time(message: Message, state: FSMContext):
    try:
        receive_text = message.text
        # Ожидаем ввод вида: 2025-07-02;10:30;13:00;Причина
        parts = receive_text.split(";")
        if len(parts) < 4:
            await message.answer("⚠️ Невірний формат! Введи так: дата;початок;кінець;причина.\n\nНаприклад:\n2025-07-02;10:30;13:00;Не хочу працювати")
            return

        date_str, start_str, end_str, reason = parts
        blocked_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
        end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

        # Проверка валидности времени
        if start_time >= end_time:
            await message.answer("⚠️ Час початку повинен бути раніше за час закінчення.")
            return

        master_id = 1  # временно фиксированный мастер
        now = datetime.now()

        pool = get_pool()
        async with pool.acquire() as conn:
            # Проверка пересечения блоков
            overlap_check = await conn.fetchval('''
                SELECT 1 FROM blocked_time
                WHERE master_id = $1
                  AND blocked_date = $2
                  AND NOT ($4 <= start_time OR $3 >= end_time)
                LIMIT 1
            ''', master_id, blocked_date, start_time, end_time)

            if overlap_check:
                await message.answer("⚠️ На цей період вже існує блокування. Повторне блокування неможливе.")
                await state.clear()
                return

            # Проверка пересечения с записями клиентов
            conflict_check = await conn.fetchval('''
                SELECT 1 FROM appointments
                WHERE master_id = $1
                  AND appointment_date = $2
                  AND stat = 'active'
                  AND NOT ($4 <= start_time OR $3 >= end_time)
                LIMIT 1
            ''', master_id, blocked_date, start_time, end_time)

            if conflict_check:
                await message.answer("⚠️ На цей час вже є активні записи клієнтів. Спочатку відмініть записи!")
                await state.clear()
                return

            # Вставка блокировки
            await conn.execute('''
                INSERT INTO blocked_time (master_id, blocked_date, start_time, end_time, reason, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', master_id, blocked_date, start_time, end_time, reason, now)

        await message.answer("✅ Час успішно заблоковано!")
        await state.clear()

    except Exception as e:
        print(f"[master_receive_blocked_time] Error: {e}")
        await message.answer("🚨 Сталася помилка при збереженні блокування.")

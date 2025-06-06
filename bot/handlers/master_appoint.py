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

#Хендлер реакции на кнопку мастера Записи. Отправляет сообщение
@router.message(F.text == BTN_MASTER_APPOINT)
async def master_appointment_hendler(message: Message, state: FSMContext):
    try:
        print(BTN_MASTER_APPOINT)
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Сьогодні", callback_data="today"), InlineKeyboardButton(text="Завтра", callback_data="tomorrow")],
            [InlineKeyboardButton(text="Тиждень", callback_data="week"), InlineKeyboardButton(text="Місяць", callback_data="month")]
        ])
        await message.answer(
            "За який період бажаєш вивести записи?\n\nОбирай нижче 👇",
            reply_markup=inline_kb 
        ) 
    except Exception as e:
        print(f"[master_appointment_hendler] Error: {e}")
        await message.answer("🚨 Сталась помилка при надсиланні повідомлення.")

#Обработка инлайн выбора Сегодня
@router.callback_query(F.data.startswith("today"))
async def choose_today(callback: CallbackQuery, state: FSMContext):
    try:
        today = date.today()
        time = datetime.now().time()
        pool = get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                                    SELECT a.id, a.appointment_date, a.start_time, a.service_id, a.client_id,
                                             s.service_name,
                                             c.full_name,
                                             cn.note
                                    FROM appointments a
                                    JOIN services s ON a.service_id = s.id
                                    JOIN clients c ON a.client_id = c.id
                                    LEFT JOIN client_notes cn ON a.client_id = cn.client_id
                                    WHERE a.appointment_date = $1
                                        AND a.start_time > $2
                                        AND a.stat = $3
                                    ORDER BY a.start_time''', today, time, 'active')
            if not rows:
                await callback.message.answer("😔 На сьогодні записів більше немає.")
                return
            response = "<b>На сьогодні є такі записи</b>\n\n"
            for row in rows:
                response += f"<b>{row['start_time'].strftime('%H:%M')}</b> - {row['service_name']} - {row['full_name']}\n"
                note = row['note']
                if note:
                    response += f"<b>Примітка:</b> {note}\n\n"
            response += f"Хочеш когось відмінити? Вибери нижче 👇"
            keyboard = []
            for row in rows:
                btn_text = f"{row['start_time'].strftime('%H:%M')}"
                callback_data = f"cancel_master;{row['id']};{row['appointment_date']};{row['start_time']}"
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
                
            await callback.message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        print(f"[choose_today] Error: {e}")
        await callback.message.answer("🚨 Сталась помилка при отриманні записів на сьогодні.") 


#Обработка инлайн выбора Завтра
@router.callback_query(F.data.startswith("tomorrow"))
async def choose_tomorrow(callback: CallbackQuery, state: FSMContext, ):
    try:
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date
        
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                                    SELECT a.id, a.appointment_date, a.start_time, a.service_id, a.client_id,
                                             s.service_name,
                                             c.full_name,
                                             cn.note
                                    FROM appointments a
                                    JOIN services s ON a.service_id = s.id
                                    JOIN clients c ON a.client_id = c.id
                                    LEFT JOIN client_notes cn ON a.client_id = cn.client_id
                                    WHERE a.appointment_date >= $1
                                        AND a.appointment_date <= $2
                                        AND a.stat = $3
                                    ORDER BY a.start_time''', start_date, end_date, 'active')
            if not rows:
                await callback.message.answer("😔 На цей період записів більше немає.")
                return
            # Группируем rows по дате
            grouped = defaultdict(list)
            for row in rows:
                grouped[row['appointment_date']].append(row)
            response = "<b>На цей період є такі записи</b>\n\n"   
            for date, records in grouped.items():
                response += f"📅 <b>Дата:</b> {date}\n"

                for row in records:
                    response += f"<b><u>{row['start_time'].strftime('%H:%M')}</u></b>\n"
                    response += f"{row['service_name']} - {row['full_name']}\n"
                    note = row['note']
                    if note:
                        response += f"📝 <b>Примітка:</b> {note}\n\n"
                response += "\n"  # отступ между датами
            
            response += f"Хочеш когось відмінити? Вибери нижче 👇"
            keyboard = []
            for row in rows:
                btn_text = f"{row['start_time'].strftime('%H:%M')}"
                callback_data = f"cancel_master;{row['id']};{row['appointment_date']};{row['start_time']}"
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
                
            await callback.message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        print(f"[choose_tomorrow] Error: {e}")
        await callback.message.answer("🚨 Сталась помилка при отриманні записів на вибраний період.") 

#Обработка инлайн выбора Тиждень
@router.callback_query(F.data.startswith("week"))
async def choose_tomorrow(callback: CallbackQuery, state: FSMContext, ):
    try:
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(weeks=1)
        
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                                    SELECT a.id, a.appointment_date, a.start_time, a.service_id, a.client_id,
                                             s.service_name,
                                             c.full_name,
                                             cn.note
                                    FROM appointments a
                                    JOIN services s ON a.service_id = s.id
                                    JOIN clients c ON a.client_id = c.id
                                    LEFT JOIN client_notes cn ON a.client_id = cn.client_id
                                    WHERE a.appointment_date >= $1
                                        AND a.appointment_date <= $2
                                        AND a.stat = $3
                                    ORDER BY a.appointment_date, a.start_time''', start_date, end_date, 'active')
            if not rows:
                await callback.message.answer("😔 На цей період записів більше немає.")
                return
            # Группируем rows по дате
            grouped = defaultdict(list)
            for row in rows:
                grouped[row['appointment_date']].append(row)
            response = "<b>На цей період є такі записи</b>\n\n"   
            for date, records in grouped.items():
                response += f"📅 <b>Дата:</b> {date}\n"

                for row in records:
                    response += f"<b><u>{row['start_time'].strftime('%H:%M')}</u></b>\n"
                    response += f"{row['service_name']} - {row['full_name']}\n"
                    note = row['note']
                    if note:
                        response += f"📝 <b>Примітка:</b> {note}\n\n"
                response += "\n"  # отступ между датами
            
            response += f"Хочеш когось відмінити? Вибери нижче 👇"
            keyboard = []
            for row in rows:
                btn_text = f"{row['appointment_date']}  {row['start_time'].strftime('%H:%M')}"
                callback_data = f"cancel_master;{row['id']};{row['appointment_date']};{row['start_time']}"
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
                
            await callback.message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        print(f"[choose_week Error: {e}")
        await callback.message.answer("🚨 Сталась помилка при отриманні записів на вибраний період.")         

#Обработка инлайн выбора Місяць
@router.callback_query(F.data.startswith("month"))
async def choose_tomorrow(callback: CallbackQuery, state: FSMContext, ):
    try:
        start_date = datetime.now()
        end_date = start_date + relativedelta(months=1)
        
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                                    SELECT a.id, a.appointment_date, a.start_time, a.service_id, a.client_id,
                                             s.service_name,
                                             c.full_name,
                                             cn.note
                                    FROM appointments a
                                    JOIN services s ON a.service_id = s.id
                                    JOIN clients c ON a.client_id = c.id
                                    LEFT JOIN client_notes cn ON a.client_id = cn.client_id
                                    WHERE a.appointment_date >= $1
                                        AND a.appointment_date <= $2
                                        AND a.stat = $3
                                    ORDER BY a.appointment_date, a.start_time''', start_date, end_date, 'active')
            if not rows:
                await callback.message.answer("😔 На цей період записів більше немає.")
                return
            # Группируем rows по дате
            grouped = defaultdict(list)
            for row in rows:
                grouped[row['appointment_date']].append(row)
            response = "<b>На цей період є такі записи</b>\n\n"   
            for date, records in grouped.items():
                response += f"📅 <b>Дата:</b> {date}\n"

                for row in records:
                    response += f"<b><u>{row['start_time'].strftime('%H:%M')}</u></b>\n"
                    response += f"{row['service_name']} - {row['full_name']}\n"
                    note = row['note']
                    if note:
                        response += f"📝 <b>Примітка:</b> {note}\n\n"
                response += "\n"  # отступ между датами
            
            response += f"Хочеш когось відмінити? Вибери нижче 👇"
            keyboard = []
            for row in rows:
                btn_text = f"{row['appointment_date']}  {row['start_time'].strftime('%H:%M')}"
                callback_data = f"cancel_master;{row['id']};{row['appointment_date']};{row['start_time']}"
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
                
            await callback.message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except Exception as e:
        print(f"[choose_month] Error: {e}")
        await callback.message.answer("🚨 Сталась помилка при отриманні записів на вибраний період.")                      
# Отменяем запись по инлайновой кнопке
@router.callback_query(F.data.startswith("cancel_master"))
async def choose_today(callback: CallbackQuery, state: FSMContext):
    try:
        _, id_str, appoint_date, start_time = callback.data.split(";")
        id = int(id_str)
        await state.update_data(
            id = id,
            appoint_date = appoint_date,
            start_time = start_time
        )
        #print(date)
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                           UPDATE appointments
                           SET stat = 'canceled_by_master'
                           WHERE id = $1
                ''', id)
        # достаём telegram_id клиента по этой записи
            row = await conn.fetchrow('''
             SELECT c.telegram_id, s.service_name
                FROM appointments a
                    JOIN clients c ON a.client_id = c.id
                    JOIN services s ON a.service_id = s.id
                WHERE a.id = $1
            ''', id)

        if row:
            client_telegram_id = row['telegram_id']
            service_name = row['service_name']
        #Отправляем подтверждение мастеру
        await callback.message.answer(f"Ти відмінила запис {appoint_date} на {start_time}")
        
        # отправляем клиенту сообщение
        await callback.bot.send_message(
        chat_id=client_telegram_id,
        text=f"❗ Ваш запис на {service_name} {appoint_date} о {start_time} був скасований майстром."
    )
    except Exception as e:
        print(f"[cancel_master] Error: {e}")
        await callback.message.answer("🚨 Сталась помилка при скасуванні запису.") 
from flask import Flask, render_template, jsonify, request
import psycopg2
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot.bot_utils import send_message_to_user
import threading

load_dotenv()
app = Flask(__name__)

def send_async_message(chat_id, service_name, time, date):
    try:
        print("Запуск отправки сообщения...")
        asyncio.run(send_message_to_user(chat_id, service_name, time, date))
        print("Сообщение отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    
    
    
@app.route("/")
def home():
    return render_template("index.html")


def get_busy_dates(year, month, duration_minutes):
    from collections import defaultdict

    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT a.appointment_date::date, a.start_time, a.end_time, 
               m.start_work_time, m.end_work_time
        FROM appointments a
        JOIN masters m ON a.master_id = m.id
        WHERE EXTRACT(YEAR FROM a.appointment_date) = %s
          AND EXTRACT(MONTH FROM a.appointment_date) = %s
    """, (year, month))

    schedule_by_date = defaultdict(list)
    work_hours_by_date = {}

    for row in cur.fetchall():
        day, start, end, master_start, master_end = row
        schedule_by_date[day].append((start, end))
        work_hours_by_date[day] = (master_start, master_end)

    cur.close()
    conn.close()

    busy_days = []

    for day in schedule_by_date:
        appointments = sorted(schedule_by_date[day])
        work_start, work_end = work_hours_by_date[day]

        current = datetime.combine(day, work_start)
        work_end_dt = datetime.combine(day, work_end)
        duration = timedelta(minutes=duration_minutes)

        free_found = False

        for appt_start, appt_end in appointments:
            appt_start_dt = datetime.combine(day, appt_start)
            appt_end_dt = datetime.combine(day, appt_end)

            if current + duration <= appt_start_dt:
                free_found = True
                break

            current = max(current, appt_end_dt)

        if not free_found and current + duration <= work_end_dt:
            free_found = True

        if not free_found:
            busy_days.append(day.isoformat())

    return busy_days

@app.route("/api/busy-days")
def busy_days():
    try:
        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
        duration = int(request.args.get("duration", 0))
    except (TypeError, ValueError):
        return jsonify([])

    busy = get_busy_dates(year, month, duration)
    return jsonify(busy)


@app.route("/api/free-slots")
def free_slots():
    try:
        date = request.args.get("date")
        duration = int(request.args.get("duration"))
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        date_obj = appointment_date.date()

        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        # Получаем рабочие часы мастера
        cur.execute("""
            SELECT start_work_time, end_work_time
            FROM masters
            LIMIT 1
        """)
        work_hours = cur.fetchone()
        if not work_hours:
            return jsonify([])

        start_work_time, end_work_time = work_hours
        work_start = datetime.combine(date_obj, start_work_time)
        work_end = datetime.combine(date_obj, end_work_time)

        # Получаем все занятые записи
        cur.execute("""
            SELECT start_time, end_time
            FROM appointments
            WHERE appointment_date::date = %s
            AND stat = %s
        """, (date_obj, "active"))
        busy_appointments = cur.fetchall()

        busy_intervals = []
        for start, end in busy_appointments:
            busy_start = datetime.combine(date_obj, start)
            busy_end = datetime.combine(date_obj, end)
            busy_intervals.append((busy_start, busy_end))
        # Получаем все блокированные интервалы
        cur.execute("""
            SELECT start_time, end_time
            FROM blocked_time
            WHERE blocked_date = %s
        """, (date_obj,))

        blocked_intervals = cur.fetchall()

        for start, end in blocked_intervals:
            blocked_start = datetime.combine(date_obj, start)
            blocked_end = datetime.combine(date_obj, end)
            busy_intervals.append((blocked_start, blocked_end))
        # Настройки интервала
        interval = timedelta(minutes=15)
        duration_delta = timedelta(minutes=duration)

        slot_time = work_start
        latest_start_time = work_end - duration_delta

        available_slots = []

        while slot_time <= latest_start_time:
            slot_end = slot_time + duration_delta

            conflict = False
            for busy_start, busy_end in busy_intervals:
                if not (slot_end <= busy_start or slot_time >= busy_end):
                    conflict = True
                    break

            if not conflict:
                available_slots.append(slot_time.strftime("%H:%M"))

            slot_time += interval

        cur.close()
        conn.close()

        return jsonify(available_slots)

    except Exception as e:
        print(f"[free_slots] Ошибка: {e}")  # Вывод в консоль
        return jsonify({"error": str(e)}), 500


# Получение данных от приложения с датой и временем записи

@app.route("/api/submit", methods=["POST"])
def submit_appointment():
    try:
        data = request.get_json()
        date = data.get("date")
        time = data.get("time")
        service_id = data.get("serviceI")  # было: seviceI
        service_name = data.get("serviceN")
        client_id = data.get("user")
        duration = data.get("duration")
        chat_id = data.get("chatID")

        start_time = datetime.strptime(time, "%H:%M")
        end_time = start_time + timedelta(minutes=duration)
        end_time_str = end_time.strftime("%H:%M")



        print(f"Получена заявка: client={client_id}, service={service_name}, date={date}, time={time}, duration={duration}")

        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        
        cur = conn.cursor()
        # Получаем название услуги по ID
        cur.execute("SELECT service_name FROM services WHERE id = %s", (service_id,))
        row = cur.fetchone()
        if row:
            service_name = row[0]
        else:
            service_name = "обрана послуга"
        cur.execute("""
            SELECT COUNT(*) FROM appointments
            WHERE appointment_date = %s
            AND start_time = %s
            AND stat = 'active'
        """, (date, time))

        conflict_count = cur.fetchone()[0]

        if conflict_count > 0:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "Цей час вже зайнятий"}), 409

# ✅ Нет конфликта — делаем запись
        query = """
    INSERT INTO appointments
    (client_id, service_id, master_id, appointment_date, start_time, end_time, stat)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
        cur.execute(query, (client_id, service_id, 1, date, time, end_time_str, "active"))
        conn.commit()
        cur.close()
        conn.close()

        # Асинхронная отправка через поток
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_message_to_user(chat_id, service_name, time, date))
        loop.close()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Ошибка при записи: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

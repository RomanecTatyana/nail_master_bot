
import psycopg2
from datetime import date, time, datetime
import os
from dotenv import load_dotenv

conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="xtcjJeoPXDGXcMiAVgHdBLXIFeymEDTd",
    host="yamabiko.proxy.rlwy.net",
    port="54475"
)

cur = conn.cursor()

# не строка, а time-объект
start = time(10, 0)
end = time(11, 0)
print(start, end)

cur.execute("""
INSERT INTO appointments (
    client_id, service_id, master_id,
    appointment_date, start_time, end_time, stat
) VALUES (%s, %s, %s, %s, %s, %s, %s)
""", (1, 1, 1, datetime(2025, 5, 22).date(), start, end, "active"))

conn.commit()
cur.close()
conn.close()



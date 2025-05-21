import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

async def create_pool():
    return await asyncpg.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

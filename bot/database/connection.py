# bot/database/connection.py

import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

_pool: asyncpg.pool.Pool = None  # глобальный пул

async def create_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            ssl='require'
        )

def get_pool():
    return _pool

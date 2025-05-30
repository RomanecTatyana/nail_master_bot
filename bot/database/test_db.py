import asyncio
from connection import create_pool

async def test():
    pool = await create_pool()
    async with pool.acquire() as connection:
        result = await connection.fetch("SELECT * FROM clients")
        for row in result:
            print(dict(row))

asyncio.run(test())

import asyncio
from app.database import engine
from sqlalchemy import inspect

async def check_tables():
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print(f"Tables: {tables}")

if __name__ == "__main__":
    asyncio.run(check_tables())

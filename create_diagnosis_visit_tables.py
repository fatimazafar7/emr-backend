import asyncio
from app.database import create_all_tables

async def main():
    print("Creating diagnosis and visits tables...")
    await create_all_tables()
    print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(main())

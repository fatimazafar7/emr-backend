import asyncio
from sqlalchemy import text
from app.database import engine

async def update_db():
    async with engine.begin() as conn:
        print("Adding record_title to medicalrecords table...")
        try:
            await conn.execute(text("ALTER TABLE medicalrecords ADD COLUMN record_title VARCHAR(255);"))
            print("Successfully added record_title column")
        except Exception as e:
            print(f"Error or column already exists: {e}")

if __name__ == "__main__":
    asyncio.run(update_db())

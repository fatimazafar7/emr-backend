import asyncio
from sqlalchemy import text
from app.database import engine

async def update_db():
    async with engine.begin() as conn:
        print("Updating prescriptions table...")
        # 1. Make doctor_id nullable in prescriptions
        await conn.execute(text("ALTER TABLE prescriptions ALTER COLUMN doctor_id DROP NOT NULL;"))
        
        # 2. Add prescribing_doctor column to prescriptions if it doesn't exist
        try:
            await conn.execute(text("ALTER TABLE prescriptions ADD COLUMN prescribing_doctor VARCHAR;"))
            print("Added prescribing_doctor column to prescriptions")
        except Exception as e:
            print(f"prescribing_doctor column might already exist: {e}")
            
        # 3. Add notes column to prescriptions if it doesn't exist
        try:
            await conn.execute(text("ALTER TABLE prescriptions ADD COLUMN notes TEXT;"))
            print("Added notes column to prescriptions")
        except Exception as e:
            print(f"notes column might already exist: {e}")

        print("\nUpdating labresults table...")
        # 4. Make doctor_id nullable in labresults
        await conn.execute(text("ALTER TABLE labresults ALTER COLUMN doctor_id DROP NOT NULL;"))
        
        # 5. Add lab_name column to labresults if it doesn't exist
        try:
            await conn.execute(text("ALTER TABLE labresults ADD COLUMN lab_name VARCHAR;"))
            print("Added lab_name column to labresults")
        except Exception as e:
            print(f"lab_name column might already exist: {e}")
            
        # 6. Add test_date column to labresults if it doesn't exist
        try:
            await conn.execute(text("ALTER TABLE labresults ADD COLUMN test_date TIMESTAMP WITH TIME ZONE;"))
            print("Added test_date column to labresults")
        except Exception as e:
            print(f"test_date column might already exist: {e}")
            
    print("\nDatabase update completed successfully!")

if __name__ == "__main__":
    asyncio.run(update_db())

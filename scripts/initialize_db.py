import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base_class import Base
from app.models.models import Clinic, User
from app.core import security
from app.core.config import settings

# Need to import all models to register with Base
from app.models.models import *

async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Caution: This drops all tables! OK for dev initial.
        await conn.run_sync(Base.metadata.create_all)
        
    print("Database tables created.")

    # Seed Default Clinic and Admin
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create Clinic
        clinic_id = uuid.UUID(settings.DEFAULT_CLINIC_ID)
        clinic = Clinic(
            id=clinic_id,
            name="EMR AI Central HQ",
            location="Global Hub",
            address="San Francisco, CA"
        )
        session.add(clinic)
        
        # Create Admin
        admin_user = User(
            clinic_id=clinic_id,
            email="admin@emr.ai",
            hashed_password=security.get_password_hash("admin123"),
            full_name="Global Administrator",
            role="admin",
            is_active=True
        )
        session.add(admin_user)
        
        await session.commit()
        print(f"Seeded Clinic: {clinic.name}")
        print(f"Seeded Admin: {admin_user.email}")

if __name__ == "__main__":
    asyncio.run(init_db())

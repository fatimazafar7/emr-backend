import asyncio
import sys
import os
import hashlib

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.clinic import Clinic
from app.database import async_session
import uuid

async def create_test_user():
    """Create a test doctor user"""
    async with async_session() as session:
        # Check if clinic exists
        from sqlalchemy import select
        clinic_result = await session.execute(select(Clinic).limit(1))
        clinic = clinic_result.scalar_one_or_none()
        
        if not clinic:
            # Create a test clinic
            clinic = Clinic(
                id=uuid.uuid4(),
                name="Test Clinic",
                address="123 Test St",
                phone="555-0123",
                email="test@clinic.com"
            )
            session.add(clinic)
            await session.flush()
        
        # Check if user already exists
        user_result = await session.execute(
            select(User).where(User.email == "doctor@test.com")
        )
        existing_user = user_result.scalar_one_or_none()
        
        if existing_user:
            print("Test user already exists:")
            print(f"  Email: {existing_user.email}")
            print(f"  Role: {existing_user.role}")
            print(f"  ID: {existing_user.id}")
            return
        
        # Create test doctor user with simple hash for testing
        password_hash = hashlib.sha256("password123".encode()).hexdigest()
        test_user = User(
            id=uuid.uuid4(),
            email="doctor@test.com",
            hashed_password=password_hash,
            first_name="Test",
            last_name="Doctor",
            role=UserRole.doctor,
            is_active=True,
            clinic_id=clinic.id
        )
        
        session.add(test_user)
        await session.commit()
        
        print("Test user created successfully!")
        print(f"  Email: doctor@test.com")
        print(f"  Password: password123")
        print(f"  Role: {test_user.role}")
        print(f"  ID: {test_user.id}")

if __name__ == "__main__":
    asyncio.run(create_test_user())

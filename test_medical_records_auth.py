#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app.database import get_db, create_all_tables
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.utils.security import create_access_token, hash_password
from sqlalchemy import select
from uuid import uuid4

async def test_medical_records_auth():
    print("🧪 Testing Medical Records Authentication...")
    
    # Create a test database session
    async for db in get_db():
        try:
            # Create tables
            await create_all_tables()
            print("✅ Database tables created")
            
            # Create test patient user
            test_user_id = uuid4()
            test_clinic_id = uuid4()
            
            test_user = User(
                id=test_user_id,
                email="test-patient@example.com",
                hashed_password=hash_password("password123"),
                first_name="Test",
                last_name="Patient",
                role=UserRole.patient,
                clinic_id=test_clinic_id
            )
            db.add(test_user)
            
            # Create patient profile
            test_patient = Patient(
                user_id=test_user_id,
                clinic_id=test_clinic_id,
                date_of_birth="1990-01-01",
                gender="other",
                blood_type="O+"
            )
            db.add(test_patient)
            
            await db.commit()
            print(f"✅ Test patient created: {test_user.email}")
            
            # Create access token
            token = create_access_token({"sub": str(test_user_id)})
            print(f"✅ Access token created: {token[:50]}...")
            
            # Test the token verification
            from app.dependencies import get_current_user
            from app.utils.security import verify_token
            
            payload = verify_token(token)
            print(f"✅ Token payload: {payload}")
            
            # Test user retrieval
            result = await db.execute(select(User).where(User.id == test_user_id))
            user = result.scalar_one_or_none()
            print(f"✅ User retrieved: {user.email}, role: {user.role}")
            
            # Test role checking
            from app.dependencies import require_role
            roles = ["doctor", "admin", "nurse", "patient"]
            role_checker = require_role(roles)
            
            try:
                checked_user = role_checker(user)
                print(f"✅ Role check passed for: {checked_user.role}")
            except Exception as e:
                print(f"❌ Role check failed: {e}")
            
            print("\n🎉 Medical records authentication test completed!")
            print(f"\n📝 Test Summary:")
            print(f"   - User ID: {test_user_id}")
            print(f"   - Email: {test_user.email}")
            print(f"   - Role: {user.role}")
            print(f"   - Token: {token[:50]}...")
            print(f"   - Patient ID: {test_patient.id}")
            
            break
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    asyncio.run(test_medical_records_auth())

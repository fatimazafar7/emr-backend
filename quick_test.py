#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.utils.security import create_access_token
from sqlalchemy import select

async def quick_test():
    print("🚀 === QUICK SYSTEM CHECK ===")
    
    async for db in get_db():
        try:
            # Check if we have a patient user with profile
            result = await db.execute(
                select(User, Patient)
                .join(Patient, User.id == Patient.user_id)
                .where(User.role == UserRole.patient)
                .limit(1)
            )
            user_patient = result.first()
            
            if user_patient:
                user, patient = user_patient
                print(f"✅ Test Patient Found: {user.email}")
                print(f"   User ID: {user.id}")
                print(f"   Patient ID: {patient.id}")
                print(f"   Clinic ID: {patient.clinic_id}")
                
                # Create test token
                token = create_access_token({"sub": str(user.id)})
                print(f"✅ Test Token: {token[:50]}...")
                
                # Test the exact API endpoint logic
                from app.routers.medical_records import create_medical_record
                from app.schemas.medical_record import MedicalRecordCreate
                from app.dependencies import get_current_user, require_role
                
                print("✅ All imports successful")
                print("🎯 System is ready for debugging!")
                
                print(f"\n📋 Test this in browser:")
                print(f"   - Login as: {user.email}")
                print(f"   - Token will be: {token[:50]}...")
                print(f"   - Patient ID: {patient.id}")
                
                return True
            else:
                print("❌ No patient user with profile found")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    if success:
        print("\n🔧 START THE SERVER NOW:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ System not ready")

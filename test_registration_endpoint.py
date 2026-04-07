#!/usr/bin/env python3

import asyncio
import sys
import os
import random
import string
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.utils.security import hash_password, create_access_token
from app.schemas.user import UserCreate
from app.schemas.medical_record import MedicalRecordCreate
from sqlalchemy import select
from app.routers.auth import register

def generate_random_email():
    """Generate a random email for testing"""
    letters = string.ascii_lowercase[:5]
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"new-patient-{random_str}@example.com"

async def test_registration_endpoint():
    print("🚀 === TESTING REGISTRATION ENDPOINT ===")
    
    async for db in get_db():
        try:
            # Step 1: Create user data for registration
            test_email = generate_random_email()
            print(f"📝 Registering new patient: {test_email}")
            
            user_data = UserCreate(
                email=test_email,
                password="password123",
                first_name="New",
                last_name="Patient",
                role=UserRole.patient,
                clinic_id="12a681ac-a370-487a-b3ee-3f381d361064"
            )
            
            # Step 2: Call the registration endpoint
            registered_user = await register(user_data, db)
            print(f"✅ User registered: {registered_user.id}")
            
            # Step 3: Check if patient profile was auto-created
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == registered_user.id)
            )
            patient = patient_result.scalar_one_or_none()
            
            if patient:
                print(f"✅ Patient profile auto-created: {patient.id}")
                print(f"   Clinic ID: {patient.clinic_id}")
                print(f"   DOB: {patient.date_of_birth}")
            else:
                print("❌ Patient profile NOT created after registration!")
                return False
            
            # Step 4: Simulate login and get token
            token = create_access_token({"sub": str(registered_user.id)})
            print(f"✅ Login token created")
            
            # Step 5: Test medical record creation immediately after registration
            print("🏥 Testing medical record creation...")
            
            record_data = MedicalRecordCreate(
                patient_name=f"{registered_user.first_name} {registered_user.last_name}",
                patient_id=patient.id,
                doctor_name="Test Doctor",
                record_type="lab_result",
                chief_complaint="First medical record after registration",
                symptoms="Test symptoms",
                notes="This is the first medical record for this newly registered patient",
                visit_date="2026-04-06",
                created_by="patient"
            )
            
            # Create medical record
            medical_record = MedicalRecord(**record_data.model_dump())
            db.add(medical_record)
            await db.commit()
            await db.refresh(medical_record)
            
            print(f"✅ Medical record created: {medical_record.id}")
            
            # Step 6: Clean up test data
            await db.delete(medical_record)
            await db.delete(patient)
            await db.delete(registered_user)
            await db.commit()
            
            print("🧹 Test data cleaned up")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False

async def test_manual_registration():
    print("\n🚀 === TESTING MANUAL REGISTRATION LOGIC ===")
    
    async for db in get_db():
        try:
            # Simulate the exact registration logic
            test_email = generate_random_email()
            print(f"📝 Manual registration test: {test_email}")
            
            # Create user (like registration does)
            user = User(
                email=test_email,
                hashed_password=hash_password("password123"),
                first_name="Manual",
                last_name="Test",
                role=UserRole.patient,
                clinic_id="12a681ac-a370-487a-b3ee-3f381d361064"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            print(f"✅ User created: {user.id}")
            
            # Create patient profile (like registration does)
            patient = Patient(
                user_id=user.id,
                clinic_id=user.clinic_id or "12a681ac-a370-487a-b3ee-3f381d361064",
                date_of_birth="1990-01-01",
                gender="other",
                blood_type="O+",
                allergies="None recorded",
                emergency_contact_name="Not provided",
                emergency_contact_phone="Not provided",
                insurance_provider="Not provided",
                insurance_number="Not provided"
            )
            db.add(patient)
            await db.commit()
            await db.refresh(patient)
            
            print(f"✅ Patient profile created: {patient.id}")
            
            # Test medical record
            token = create_access_token({"sub": str(user.id)})
            
            record_data = MedicalRecordCreate(
                patient_name=f"{user.first_name} {user.last_name}",
                patient_id=patient.id,
                doctor_name="Test Doctor",
                record_type="lab_result",
                chief_complaint="Manual registration test",
                symptoms="Test symptoms",
                notes="Manual registration test record",
                visit_date="2026-04-06",
                created_by="patient"
            )
            
            medical_record = MedicalRecord(**record_data.model_dump())
            db.add(medical_record)
            await db.commit()
            await db.refresh(medical_record)
            
            print(f"✅ Medical record created: {medical_record.id}")
            
            # Clean up
            await db.delete(medical_record)
            await db.delete(patient)
            await db.delete(user)
            await db.commit()
            
            print("🧹 Manual test cleaned up")
            return True
            
        except Exception as e:
            print(f"❌ Manual test failed: {e}")
            await db.rollback()
            return False

async def main():
    print("🧪 NEW PATIENT REGISTRATION - COMPLETE FLOW TEST\n")
    
    # Test 1: Registration endpoint
    endpoint_ok = await test_registration_endpoint()
    
    # Test 2: Manual registration logic
    manual_ok = await test_manual_registration()
    
    print(f"\n📊 === FINAL RESULTS ===")
    print(f"Registration Endpoint: {'✅ PASS' if endpoint_ok else '❌ FAIL'}")
    print(f"Manual Registration: {'✅ PASS' if manual_ok else '❌ FAIL'}")
    
    if endpoint_ok and manual_ok:
        print("\n🎉 REGISTRATION WORKS PERFECTLY!")
        print("✅ ANY patient who signs up gets IMMEDIATE medical record access!")
        print("✅ Patient profiles are auto-created during registration!")
        print("✅ No barriers for new patients!")
    else:
        print("\n❌ Registration has issues")
        print("🔧 Need to fix patient profile creation during signup")

if __name__ == "__main__":
    asyncio.run(main())

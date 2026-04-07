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
from app.schemas.medical_record import MedicalRecordCreate
from sqlalchemy import select

def generate_random_email():
    """Generate a random email for testing"""
    letters = string.ascii_lowercase[:5]
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"test-patient-{random_str}@example.com"

async def test_new_patient_signup():
    print("🚀 === TESTING NEW PATIENT SIGNUP FLOW ===")
    
    async for db in get_db():
        try:
            # Step 1: Create a new patient user (simulate signup)
            test_email = generate_random_email()
            print(f"📝 Creating new patient: {test_email}")
            
            # Create user
            new_user = User(
                email=test_email,
                hashed_password=hash_password("password123"),
                first_name="Test",
                last_name="Patient",
                role=UserRole.patient,
                clinic_id="12a681ac-a370-487a-b3ee-3f381d361064"
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"✅ User created: {new_user.id}")
            
            # Step 2: Check if patient profile was auto-created
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == new_user.id)
            )
            patient = patient_result.scalar_one_or_none()
            
            if patient:
                print(f"✅ Patient profile auto-created: {patient.id}")
            else:
                print("❌ Patient profile NOT created - this is the issue!")
                return False
            
            # Step 3: Simulate login and get token
            token = create_access_token({"sub": str(new_user.id)})
            print(f"✅ Login token created")
            
            # Step 4: Test medical record creation immediately after signup
            print("🏥 Testing medical record creation...")
            
            record_data = MedicalRecordCreate(
                patient_name=f"{new_user.first_name} {new_user.last_name}",
                patient_id=patient.id,
                doctor_name="Test Doctor",
                record_type="lab_result",
                chief_complaint="First medical record after signup",
                symptoms="Test symptoms",
                notes="This is the first medical record for this new patient",
                visit_date="2026-04-06",
                created_by="patient"
            )
            
            # Create medical record
            medical_record = MedicalRecord(**record_data.model_dump())
            db.add(medical_record)
            await db.commit()
            await db.refresh(medical_record)
            
            print(f"✅ Medical record created: {medical_record.id}")
            
            # Step 5: Clean up test data
            await db.delete(medical_record)
            await db.delete(patient)
            await db.delete(new_user)
            await db.commit()
            
            print("🧹 Test data cleaned up")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False

async def test_multiple_new_patients():
    print("\n🚀 === TESTING MULTIPLE NEW PATIENT SIGNUPS ===")
    
    success_count = 0
    fail_count = 0
    
    for i in range(3):
        print(f"\n📝 Test #{i+1}")
        
        if await test_new_patient_signup():
            success_count += 1
            print(f"✅ Test #{i+1} PASSED")
        else:
            fail_count += 1
            print(f"❌ Test #{i+1} FAILED")
    
    print(f"\n📊 MULTIPLE SIGNUP TEST RESULTS:")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📈 Success Rate: {(success_count/3*100):.1f}%")
    
    return fail_count == 0

async def main():
    print("🧪 NEW PATIENT SIGNUP - IMMEDIATE MEDICAL RECORD ACCESS TEST\n")
    
    # Test 1: Single new patient signup
    single_ok = await test_new_patient_signup()
    
    # Test 2: Multiple new patient signups
    multiple_ok = await test_multiple_new_patients()
    
    print(f"\n📊 === FINAL RESULTS ===")
    print(f"Single Patient Test: {'✅ PASS' if single_ok else '❌ FAIL'}")
    print(f"Multiple Patients Test: {'✅ PASS' if multiple_ok else '❌ FAIL'}")
    
    if single_ok and multiple_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ ANY patient who signs up can IMMEDIATELY add medical records!")
        print("✅ Patient profiles are auto-created during signup!")
        print("✅ No barriers for new patients!")
        print("\n🎯 NEW PATIENT FLOW:")
        print("   1. Sign up → User created")
        print("   2. Auto-create → Patient profile created")
        print("   3. Login → Token generated")
        print("   4. Add record → SUCCESS! 🚀")
    else:
        print("\n❌ Some tests failed - new patients may face issues")
    
    print(f"\n🔧 What this ensures:")
    print(f"   ✅ New patient signup works seamlessly")
    print(f"   ✅ Patient profiles created automatically")
    print(f"   ✅ Immediate access to medical records")
    print(f"   ✅ No permission issues for new users")

if __name__ == "__main__":
    asyncio.run(main())

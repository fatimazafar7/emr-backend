#!/usr/bin/env python3

import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, engine
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.utils.security import create_access_token, hash_password
from sqlalchemy import select, text
from uuid import uuid4
from app.config import settings

async def test_database_connectivity():
    print("🔍 === DATABASE CONNECTIVITY TEST ===")
    
    try:
        # Test basic database connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ Database connection successful: {result.scalar()}")
            
        # Test table existence
        async for db in get_db():
            # Check users table
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"✅ Users table accessible: {user_count} users found")
            
            # Check patients table
            result = await db.execute(text("SELECT COUNT(*) FROM patients"))
            patient_count = result.scalar()
            print(f"✅ Patients table accessible: {patient_count} patients found")
            
            # Check medical_records table
            result = await db.execute(text("SELECT COUNT(*) FROM medical_records"))
            record_count = result.scalar()
            print(f"✅ Medical records table accessible: {record_count} records found")
            
            break
            
    except Exception as e:
        print(f"❌ Database connectivity error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_existing_patient():
    print("\n🔍 === EXISTING PATIENT TEST ===")
    
    async for db in get_db():
        try:
            # Find a patient user with patient profile
            result = await db.execute(
                select(User, Patient)
                .join(Patient, User.id == Patient.user_id)
                .where(User.role == UserRole.patient)
                .limit(1)
            )
            user_patient = result.first()
            
            if user_patient:
                user, patient = user_patient
                print(f"✅ Found patient user: {user.email}")
                print(f"   User ID: {user.id}")
                print(f"   Role: {user.role}")
                print(f"   Patient ID: {patient.id}")
                print(f"   Clinic ID: {patient.clinic_id}")
                
                # Create test token
                token = create_access_token({"sub": str(user.id)})
                print(f"✅ Test token created: {token[:50]}...")
                
                return {
                    'user': user,
                    'patient': patient,
                    'token': token
                }
            else:
                print("❌ No patient with patient profile found")
                return None
                
        except Exception as e:
            print(f"❌ Error finding patient: {e}")
            import traceback
            traceback.print_exc()
            return None

async def test_medical_record_creation(test_data):
    print("\n🔍 === MEDICAL RECORD CREATION TEST ===")
    
    if not test_data:
        print("❌ No test data available")
        return False
    
    user, patient, token = test_data['user'], test_data['patient'], test_data['token']
    
    try:
        # Simulate the medical record creation logic
        from app.routers.medical_records import create_medical_record
        from app.schemas.medical_record import MedicalRecordCreate
        
        # Create test medical record data
        record_data = MedicalRecordCreate(
            patient_name=f"{user.first_name} {user.last_name}",
            patient_id=patient.id,
            doctor_name="Test Doctor",
            record_type="lab_result",
            chief_complaint="Test complaint",
            symptoms="Test symptoms",
            notes="Test notes",
            visit_date="2026-04-06",
            created_by="patient"
        )
        
        print(f"📝 Test record data: {record_data.dict()}")
        
        # Test database insertion directly
        async for db in get_db():
            try:
                medical_record = MedicalRecord(**record_data.dict())
                db.add(medical_record)
                await db.commit()
                await db.refresh(medical_record)
                
                print(f"✅ Medical record created successfully: {medical_record.id}")
                print(f"   Patient ID: {medical_record.patient_id}")
                print(f"   Record Type: {medical_record.record_type}")
                print(f"   Chief Complaint: {medical_record.chief_complaint}")
                
                # Clean up test record
                await db.delete(medical_record)
                await db.commit()
                print("🧹 Test record cleaned up")
                
                return True
                
            except Exception as e:
                print(f"❌ Error creating medical record: {e}")
                await db.rollback()
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Error in medical record test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoint():
    print("\n🔍 === API ENDPOINT TEST ===")
    
    try:
        # Test if the FastAPI app can be imported and configured
        from app.main import app
        print(f"✅ FastAPI app created: {app.title}")
        
        # Check if medical records router is included
        routes = [route for route in app.routes if hasattr(route, 'path') and 'medical-records' in route.path]
        print(f"✅ Medical records routes found: {len(routes)}")
        
        for route in routes:
            print(f"   - {route.methods} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 === COMPREHENSIVE STACK TEST ===\n")
    
    # Test 1: Database Connectivity
    db_ok = await test_database_connectivity()
    
    # Test 2: Existing Patient
    patient_data = await test_existing_patient()
    
    # Test 3: Medical Record Creation
    record_ok = await test_medical_record_creation(patient_data)
    
    # Test 4: API Endpoints
    api_ok = await test_api_endpoint()
    
    # Summary
    print("\n📊 === TEST SUMMARY ===")
    print(f"Database Connectivity: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Patient Data Available: {'✅ PASS' if patient_data else '❌ FAIL'}")
    print(f"Medical Record Creation: {'✅ PASS' if record_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if all([db_ok, patient_data, record_ok, api_ok]):
        print("\n🎉 ALL TESTS PASSED - Stack is working correctly!")
        print("💡 The issue might be in frontend authentication or request handling")
    else:
        print("\n❌ SOME TESTS FAILED - Check the errors above")
    
    print(f"\n🔧 Configuration:")
    print(f"   Database URL: {settings.DATABASE_URL}")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   API Prefix: {settings.API_V1_STR}")

if __name__ == "__main__":
    asyncio.run(main())

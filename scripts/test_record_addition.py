import asyncio
import sys
import os
from uuid import UUID

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.lab_result import LabResult
from sqlalchemy import select

async def test_prescription_addition():
    print("🚀 Testing Prescription Addition for Patient...")
    
    async for db in get_db():
        try:
            # 1. Find a patient user
            result = await db.execute(
                select(User).where(User.role == UserRole.patient).limit(1)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ No patient user found in database.")
                return False
                
            print(f"👤 Using patient user: {user.email}")
            
            # 2. Get patient profile
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == user.id)
            )
            patient = patient_result.scalar_one_or_none()
            
            if not patient:
                print(f"❌ No patient profile found for {user.email}")
                return False
            
            # 3. Test Prescription creation with NULL doctor_id and new fields
            print("📝 Creating test prescription...")
            prescription = Prescription(
                patient_id=patient.id,
                doctor_id=None,  # Nullable now!
                medication_name="Test Amoxicillin",
                dosage="500mg",
                frequency="Three times daily",
                prescribing_doctor="Dr. External Smith",
                notes="Test notes for external prescription",
                is_active=True
            )
            
            db.add(prescription)
            await db.commit()
            await db.refresh(prescription)
            print(f"✅ Prescription created successfully! ID: {prescription.id}")
            
            # 4. Test Lab Result creation with NULL doctor_id and new fields
            print("📝 Creating test lab result...")
            lab_result = LabResult(
                patient_id=patient.id,
                doctor_id=None,  # Nullable now!
                test_name="Full Blood Count",
                lab_name="City Central Lab",
                result_value="Normal",
                notes="External lab result test"
            )
            
            db.add(lab_result)
            await db.commit()
            await db.refresh(lab_result)
            print(f"✅ Lab Result created successfully! ID: {lab_result.id}")
            
            # 5. Clean up
            await db.delete(prescription)
            await db.delete(lab_result)
            await db.commit()
            print("🧹 Test data cleaned up.")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False

if __name__ == "__main__":
    asyncio.run(test_prescription_addition())

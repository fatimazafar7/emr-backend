from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse


class PatientService:
    @staticmethod
    async def get_all_patients(db: AsyncSession, clinic_id: Optional[UUID] = None) -> List[Patient]:
        query = select(Patient)
        if clinic_id:
            query = query.where(Patient.clinic_id == clinic_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_patient_by_id(db: AsyncSession, patient_id: UUID) -> Optional[Patient]:
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_patient_by_user_id(db: AsyncSession, user_id: UUID) -> Optional[Patient]:
        result = await db.execute(select(Patient).where(Patient.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_or_create_patient_by_user_id(db: AsyncSession, user_id: UUID, clinic_id: Optional[UUID] = None) -> Patient:
        patient = await PatientService.get_patient_by_user_id(db, user_id)
        if patient:
            return patient
        
        # Create default patient profile
        print(f"🔧 Service: Auto-creating patient profile for user_id: {user_id}")
        # Default clinic ID if not provided
        cid = clinic_id or UUID("12a681ac-a370-487a-b3ee-3f381d361064")
        
        patient = Patient(
            user_id=user_id,
            clinic_id=cid,
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
        print(f"✅ Service: Created patient profile: {patient.id}")
        return patient

    @staticmethod
    async def create_patient(db: AsyncSession, patient_data: PatientCreate) -> Patient:
        patient = Patient(**patient_data.dict())
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def update_patient(db: AsyncSession, patient_id: UUID, patient_data: PatientUpdate) -> Optional[Patient]:
        patient = await PatientService.get_patient_by_id(db, patient_id)
        if not patient:
            return None
        
        for key, value in patient_data.dict(exclude_unset=True).items():
            setattr(patient, key, value)
        
        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def delete_patient(db: AsyncSession, patient_id: UUID) -> bool:
        patient = await PatientService.get_patient_by_id(db, patient_id)
        if not patient:
            return False
        
        await db.delete(patient)
        await db.commit()
        return True
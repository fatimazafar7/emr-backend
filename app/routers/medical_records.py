from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.medical_record import MedicalRecordResponse, MedicalRecordCreate, MedicalRecordUpdate
from app.models.medical_record import MedicalRecord
from app.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[MedicalRecordResponse])
async def get_medical_records(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "nurse", "patient"]))
):
    # Filter records based on user role
    if user.role == "patient":
        # Patients can only see their own records - need to find their patient_id first
        from app.models.patient import Patient
        patient_result = await db.execute(
            select(Patient).where(Patient.user_id == user.id)
        )
        patient = patient_result.scalar_one_or_none()
        
        if patient:
            result = await db.execute(
                select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
            )
        else:
            result = await db.execute(select(MedicalRecord).where(False))  # Return empty
    elif user.role == "doctor":
        # Doctors can see records where they are the doctor
        result = await db.execute(
            select(MedicalRecord).where(MedicalRecord.doctor_id == user.id)
        )
    else:
        # Admin and nurses can see all records
        result = await db.execute(select(MedicalRecord))
    
    return result.scalars().all()

@router.get("/{id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    return record

from app.services.patient_service import PatientService

@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    record_in: MedicalRecordCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "nurse", "patient"]))
):
    # Handle different user types
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        
        # Override patient_id with the actual patient record ID
        record_in.patient_id = patient.id
        
        # Set patient_name if not provided
        if not record_in.patient_name:
            record_in.patient_name = f"{user.first_name} {user.last_name}"
        
        # Set created_by
        record_in.created_by = "patient"
        
    elif user.role == "doctor":
        # Doctors can create records for any patient
        if not record_in.patient_id:
            raise HTTPException(
                status_code=400, 
                detail="Patient ID is required when doctor creates medical record"
            )
        
        # Set doctor information
        if not record_in.doctor_id:
            from app.models.doctor import Doctor
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == user.id)
            )
            doctor = doctor_result.scalar_one_or_none()
            if doctor:
                record_in.doctor_id = doctor.id
        
        if not record_in.doctor_name:
            record_in.doctor_name = f"{user.first_name} {user.last_name}"
        
        record_in.created_by = "doctor"
        
    elif user.role in ["admin", "nurse"]:
        # Admins and nurses can create records
        record_in.created_by = user.role
    
    # Create the medical record
    medical_record = MedicalRecord(**record_in.model_dump())
    db.add(medical_record)
    await db.commit()
    await db.refresh(medical_record)
    
    return medical_record

@router.put("/{id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    id: UUID,
    record_in: MedicalRecordUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    
    for key, value in record_in.dict(exclude_unset=True).items():
        setattr(record, key, value)
    
    await db.commit()
    await db.refresh(record)
    return record

@router.delete("/{id}")
async def delete_medical_record(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical Record not found")
    
    await db.delete(record)
    await db.commit()
    return {"status": "ok"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.diagnosis import DiagnosisResponse, DiagnosisCreate, DiagnosisUpdate
from app.models.diagnosis import Diagnosis
from app.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[DiagnosisResponse])
async def get_diagnoses(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "nurse", "patient"]))
):
    # Filter diagnoses based on user role
    if user.role == "patient":
        # Patients can only see their own diagnoses - need to find their patient_id first
        from app.models.patient import Patient
        patient_result = await db.execute(
            select(Patient).where(Patient.user_id == user.id)
        )
        patient = patient_result.scalar_one_or_none()
        
        if patient:
            result = await db.execute(
                select(Diagnosis).where(Diagnosis.patient_id == patient.id)
            )
        else:
            result = await db.execute(select(Diagnosis).where(False))  # Return empty
    else:
        # Doctors, admins, nurses can see all diagnoses
        result = await db.execute(select(Diagnosis))
    
    return result.scalars().all()

@router.get("/{id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Diagnosis).where(Diagnosis.id == id))
    diagnosis = result.scalar_one_or_none()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return diagnosis

from app.services.patient_service import PatientService

@router.post("/", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    diagnosis_in: DiagnosisCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"]))
):
    # If user is patient, force patient_id from their profile
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        
        # Force the patient_id to match the logged-in patient
        diagnosis_data = diagnosis_in.dict()
        diagnosis_data["patient_id"] = patient.id
        diagnosis = Diagnosis(**diagnosis_data)
    else:
        # Doctors and admins can create diagnoses for any patient
        diagnosis = Diagnosis(**diagnosis_in.dict())
    
    db.add(diagnosis)
    await db.commit()
    await db.refresh(diagnosis)
    return diagnosis

@router.put("/{id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    id: UUID,
    diagnosis_in: DiagnosisUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(Diagnosis).where(Diagnosis.id == id))
    diagnosis = result.scalar_one_or_none()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    for key, value in diagnosis_in.dict(exclude_unset=True).items():
        setattr(diagnosis, key, value)
    
    await db.commit()
    await db.refresh(diagnosis)
    return diagnosis

@router.delete("/{id}")
async def delete_diagnosis(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(Diagnosis).where(Diagnosis.id == id))
    diagnosis = result.scalar_one_or_none()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    await db.delete(diagnosis)
    await db.commit()
    return {"status": "ok", "message": "Diagnosis deleted"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.prescription import PrescriptionResponse, PrescriptionCreate, PrescriptionUpdate
from app.models.prescription import Prescription
from app.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[PrescriptionResponse])
async def get_prescriptions(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "nurse", "patient"]))
):
    # Filter prescriptions based on user role
    if user.role == "patient":
        # Patients can only see their own prescriptions - need to find their patient_id first
        from app.models.patient import Patient
        patient_result = await db.execute(
            select(Patient).where(Patient.user_id == user.id)
        )
        patient = patient_result.scalar_one_or_none()
        
        if patient:
            result = await db.execute(
                select(Prescription).where(Prescription.patient_id == patient.id)
            )
        else:
            result = await db.execute(select(Prescription).where(False))  # Return empty
    else:
        # Doctors, admins, nurses can see all prescriptions
        result = await db.execute(select(Prescription))
    
    return result.scalars().all()

@router.get("/{id}", response_model=PrescriptionResponse)
async def get_prescription(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Prescription).where(Prescription.id == id))
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

from app.services.patient_service import PatientService

@router.post("/", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_in: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"]))
):
    # If user is patient, force patient_id from their profile
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        
        # Force the patient_id to match the logged-in patient
        prescription_data = prescription_in.dict()
        prescription_data["patient_id"] = patient.id
        prescription = Prescription(**prescription_data)
    else:
        # Doctors and admins can create prescriptions for any patient
        prescription = Prescription(**prescription_in.dict())
    
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    return prescription

@router.put("/{id}", response_model=PrescriptionResponse)
async def update_prescription(
    id: UUID,
    prescription_in: PrescriptionUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(Prescription).where(Prescription.id == id))
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    for key, value in prescription_in.dict(exclude_unset=True).items():
        setattr(prescription, key, value)
    
    await db.commit()
    await db.refresh(prescription)
    return prescription

@router.patch("/{id}/deactivate")
async def deactivate_prescription(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(Prescription).where(Prescription.id == id))
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    prescription.is_active = False
    await db.commit()
    return {"status": "ok", "message": "Prescription deactivated"}

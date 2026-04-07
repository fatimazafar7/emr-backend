from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.lab_result import LabResultResponse, LabResultCreate, LabResultUpdate
from app.models.lab_result import LabResult
from app.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[LabResultResponse])
async def get_lab_results(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "nurse", "patient"]))
):
    # Filter lab results based on user role
    if user.role == "patient":
        # Patients can only see their own lab results - need to find their patient_id first
        from app.models.patient import Patient
        patient_result = await db.execute(
            select(Patient).where(Patient.user_id == user.id)
        )
        patient = patient_result.scalar_one_or_none()
        
        if patient:
            result = await db.execute(
                select(LabResult).where(LabResult.patient_id == patient.id)
            )
        else:
            result = await db.execute(select(LabResult).where(False))  # Return empty
    else:
        # Doctors, admins, nurses can see all lab results
        result = await db.execute(select(LabResult))
    
    return result.scalars().all()

@router.get("/{id}", response_model=LabResultResponse)
async def get_lab_result(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(LabResult).where(LabResult.id == id))
    lab_result = result.scalar_one_or_none()
    if not lab_result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    return lab_result

from app.services.patient_service import PatientService

@router.post("/", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_result(
    lab_result_in: LabResultCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"]))
):
    # If user is patient, force patient_id from their profile
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        
        # Force the patient_id to match the logged-in patient
        lab_result_data = lab_result_in.dict()
        lab_result_data["patient_id"] = patient.id
        lab_result = LabResult(**lab_result_data)
    else:
        # Doctors and admins can create lab results for any patient
        lab_result = LabResult(**lab_result_in.dict())
    
    db.add(lab_result)
    await db.commit()
    await db.refresh(lab_result)
    return lab_result

@router.put("/{id}", response_model=LabResultResponse)
async def update_lab_result(
    id: UUID,
    lab_result_in: LabResultUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(LabResult).where(LabResult.id == id))
    lab_result = result.scalar_one_or_none()
    if not lab_result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    
    for key, value in lab_result_in.dict(exclude_unset=True).items():
        setattr(lab_result, key, value)
    
    await db.commit()
    await db.refresh(lab_result)
    return lab_result

@router.patch("/{id}/status")
async def update_lab_result_status(
    id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(LabResult).where(LabResult.id == id))
    lab_result = result.scalar_one_or_none()
    if not lab_result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    
    lab_result.status = status
    await db.commit()
    return {"status": "ok", "message": "status updated"}

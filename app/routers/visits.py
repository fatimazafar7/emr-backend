from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.visit import VisitResponse, VisitCreate, VisitUpdate
from app.models.visit import Visit
from app.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[VisitResponse])
async def get_visits(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "nurse", "patient"]))
):
    # Filter visits based on user role
    if user.role == "patient":
        # Patients can only see their own visits - need to find their patient_id first
        from app.models.patient import Patient
        patient_result = await db.execute(
            select(Patient).where(Patient.user_id == user.id)
        )
        patient = patient_result.scalar_one_or_none()
        
        if patient:
            result = await db.execute(
                select(Visit).where(Visit.patient_id == patient.id)
            )
        else:
            result = await db.execute(select(Visit).where(False))  # Return empty
    else:
        # Doctors, admins, nurses can see all visits
        result = await db.execute(select(Visit))
    
    return result.scalars().all()

@router.get("/{id}", response_model=VisitResponse)
async def get_visit(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Visit).where(Visit.id == id))
    visit = result.scalar_one_or_none()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

from app.services.patient_service import PatientService

@router.post("/", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    visit_in: VisitCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"]))
):
    # If user is patient, force patient_id from their profile
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        
        # Force the patient_id to match the logged-in patient
        visit_data = visit_in.dict()
        visit_data["patient_id"] = patient.id
        visit = Visit(**visit_data)
    else:
        # Doctors and admins can create visits for any patient
        visit = Visit(**visit_in.dict())
    
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return visit

@router.put("/{id}", response_model=VisitResponse)
async def update_visit(
    id: UUID,
    visit_in: VisitUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(Visit).where(Visit.id == id))
    visit = result.scalar_one_or_none()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    for key, value in visit_in.dict(exclude_unset=True).items():
        setattr(visit, key, value)
    
    await db.commit()
    await db.refresh(visit)
    return visit

@router.delete("/{id}")
async def delete_visit(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(Visit).where(Visit.id == id))
    visit = result.scalar_one_or_none()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    await db.delete(visit)
    await db.commit()
    return {"status": "ok", "message": "Visit deleted"}

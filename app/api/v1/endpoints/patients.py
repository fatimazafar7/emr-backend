from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Any, List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.models import Patient
from app.schemas.schemas import PatientOut, PatientCreate, PatientBase
from pydantic import UUID4
import uuid

router = APIRouter()

@router.get("/", response_model=List[PatientOut])
async def read_patients(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    clinic_id: Optional[str] = None
) -> Any:
    """
    Retrieve patients with clinic-level isolation.
    """
    # Real multi-tenancy implementation will extract clinic_id from JWT
    query = select(Patient)
    if clinic_id:
        query = query.where(Patient.clinic_id == uuid.UUID(clinic_id))
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{id}", response_model=PatientOut)
async def read_patient(
    id: UUID4,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific patient by biological ID.
    """
    result = await db.execute(select(Patient).where(Patient.id == id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found on this node")
    return patient

@router.post("/", response_model=PatientOut)
async def create_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new biological entity into the clinical registry.
    """
    patient = Patient(**patient_in.dict())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient

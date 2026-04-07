from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas.clinic import ClinicResponse, ClinicCreate, ClinicUpdate
from app.models.clinic import Clinic
from app.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[ClinicResponse])
async def get_clinics(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Clinic))
    return result.scalars().all()

@router.get("/{id}", response_model=ClinicResponse)
async def get_clinic(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Clinic).where(Clinic.id == id))
    clinic = result.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic

@router.post("/", response_model=ClinicResponse)
async def create_clinic(
    clinic_in: ClinicCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    clinic = Clinic(**clinic_in.dict())
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic

@router.put("/{id}", response_model=ClinicResponse)
async def update_clinic(
    id: str,
    clinic_in: ClinicUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    result = await db.execute(select(Clinic).where(Clinic.id == id))
    clinic = result.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    for key, value in clinic_in.dict(exclude_unset=True).items():
        setattr(clinic, key, value)
    
    await db.commit()
    await db.refresh(clinic)
    return clinic

@router.delete("/{id}")
async def delete_clinic(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    result = await db.execute(select(Clinic).where(Clinic.id == id))
    clinic = result.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    await db.delete(clinic)
    await db.commit()
    return {"status": "ok"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas.vital import VitalResponse, VitalCreate, VitalUpdate
from app.models.vital import Vital
from app.dependencies import get_current_user, require_role

router = APIRouter()

from app.services.patient_service import PatientService
from uuid import UUID

@router.get("/patient/{patient_id}", response_model=List[VitalResponse])
async def get_patient_vitals(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    # If the user is a patient, resolve their patient_id from user.id
    # even if they provided their user_id instead of patient_id
    if user.role == "patient" and (str(user.id) == patient_id or patient_id == "me"):
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        query_id = patient.id
    else:
        try:
            query_id = UUID(patient_id)
        except ValueError:
            # Maybe it's a user ID, let's check
            try:
                user_uuid = UUID(patient_id)
                patient = await PatientService.get_patient_by_user_id(db, user_uuid)
                if patient:
                    query_id = patient.id
                else:
                    raise HTTPException(status_code=404, detail="Patient profile not found for this user ID")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid patient ID format")

    result = await db.execute(select(Vital).where(Vital.patient_id == query_id))
    return result.scalars().all()

@router.post("/", response_model=VitalResponse)
async def create_vital(
    vital_in: VitalCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    vital_data = vital_in.dict()
    
    # If the user is a patient, ensure patient_id and recorded_by are correct
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        vital_data["patient_id"] = patient.id
        vital_data["recorded_by"] = user.id
    else:
        # For non-patients, ensure recorded_by is set to the current user if not provided
        if not vital_data.get("recorded_by"):
            vital_data["recorded_by"] = user.id
            
    vital = Vital(**vital_data)
    db.add(vital)
    await db.commit()
    await db.refresh(vital)
    return vital

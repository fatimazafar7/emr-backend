from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.patient import PatientResponse, PatientCreate, PatientUpdate
from app.models.patient import Patient
from app.models.user import User
from app.dependencies import get_current_user, require_role
from app.services.patient_service import PatientService

router = APIRouter()

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"])),
    clinic_id: Optional[str] = Query(None, description="Filter by clinic ID")
):
    # Filter patients based on user role
    if user.role == "patient":
        # Patients can only see their own record
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        patients = [patient]
    elif clinic_id:
        try:
            clinic_uuid = UUID(clinic_id)
            patients = await PatientService.get_all_patients(db, clinic_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid clinic ID format")
    else:
        patients = await PatientService.get_all_patients(db)
    
    # Include user information in response
    result_patients = []
    for patient in patients:
        # Get user information
        user_result = await db.execute(select(User).where(User.id == patient.user_id))
        patient_user = user_result.scalar_one_or_none()
        
        patient_dict = {
            "id": patient.id,
            "user_id": patient.user_id,
            "clinic_id": patient.clinic_id,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "blood_type": patient.blood_type,
            "allergies": patient.allergies,
            "emergency_contact_name": patient.emergency_contact_name,
            "emergency_contact_phone": patient.emergency_contact_phone,
            "insurance_provider": patient.insurance_provider,
            "insurance_number": patient.insurance_number,
            "user": {
                "id": patient_user.id,
                "first_name": patient_user.first_name,
                "last_name": patient_user.last_name,
                "email": patient_user.email
            } if patient_user else None
        }
        result_patients.append(PatientResponse(**patient_dict))
    
    return result_patients

@router.get("/me", response_model=PatientResponse)
async def get_me_patient(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.role != "patient":
        # Check if they are a doctor
        if user.role == "doctor":
             raise HTTPException(status_code=404, detail="Is a doctor, not a patient")
        raise HTTPException(status_code=403, detail="Not a patient")

    patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
    
    # Include user information
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "clinic_id": patient.clinic_id,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender or "other",
        "blood_type": patient.blood_type or "O+",
        "allergies": patient.allergies or "None recorded",
        "emergency_contact_name": patient.emergency_contact_name or "Not provided",
        "emergency_contact_phone": patient.emergency_contact_phone or "Not provided",
        "insurance_provider": patient.insurance_provider or "Not provided",
        "insurance_number": patient.insurance_number or "Not provided",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }
    }
    return PatientResponse(**patient_dict)

@router.get("/{id}", response_model=PatientResponse)
async def get_patient(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        patient_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    patient = await PatientService.get_patient_by_id(db, patient_uuid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Include user information
    user_result = await db.execute(select(User).where(User.id == patient.user_id))
    patient_user = user_result.scalar_one_or_none()
    
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "clinic_id": patient.clinic_id,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "blood_type": patient.blood_type,
        "allergies": patient.allergies,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "insurance_provider": patient.insurance_provider,
        "insurance_number": patient.insurance_number,
        "user": {
            "id": patient_user.id,
            "first_name": patient_user.first_name,
            "last_name": patient_user.last_name,
            "email": patient_user.email
        } if patient_user else None
    }
    return PatientResponse(**patient_dict)

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    patient = await PatientService.create_patient(db, patient_in)
    
    # Include user information in response
    user_result = await db.execute(select(User).where(User.id == patient.user_id))
    patient_user = user_result.scalar_one_or_none()
    
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "clinic_id": patient.clinic_id,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "blood_type": patient.blood_type,
        "allergies": patient.allergies,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "insurance_provider": patient.insurance_provider,
        "insurance_number": patient.insurance_number,
        "user": {
            "id": patient_user.id,
            "first_name": patient_user.first_name,
            "last_name": patient_user.last_name,
            "email": patient_user.email
        } if patient_user else None
    }
    return PatientResponse(**patient_dict)

@router.put("/{id}", response_model=PatientResponse)
async def update_patient(
    id: str,
    patient_in: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"]))
):
    try:
        patient_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    # If user is a patient, ensure they are only updating THEIR OWN record
    if user.role == "patient":
        existing_patient = await PatientService.get_patient_by_id(db, patient_uuid)
        if not existing_patient or existing_patient.user_id != user.id:
            raise HTTPException(
                status_code=403, 
                detail="You are not authorized to update this patient record"
            )

    patient = await PatientService.update_patient(db, patient_uuid, patient_in)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Include user information in response
    user_result = await db.execute(select(User).where(User.id == patient.user_id))
    patient_user = user_result.scalar_one_or_none()
    
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "clinic_id": patient.clinic_id,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "blood_type": patient.blood_type,
        "allergies": patient.allergies,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "insurance_provider": patient.insurance_provider,
        "insurance_number": patient.insurance_number,
        "user": {
            "id": patient_user.id,
            "first_name": patient_user.first_name,
            "last_name": patient_user.last_name,
            "email": patient_user.email
        } if patient_user else None
    }
    return PatientResponse(**patient_dict)

@router.delete("/{id}")
async def delete_patient(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    try:
        patient_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")
    
    success = await PatientService.delete_patient(db, patient_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {"status": "ok", "message": "Patient deleted successfully"}

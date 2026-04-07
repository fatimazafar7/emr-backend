from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.doctor import DoctorResponse, DoctorCreate, DoctorUpdate
from app.models.doctor import Doctor
from app.models.user import User
from app.dependencies import get_current_user, require_role
from app.services.doctor_service import DoctorService

router = APIRouter()

@router.get("/", response_model=List[DoctorResponse])
async def get_doctors(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    clinic_id: Optional[str] = Query(None, description="Filter by clinic ID")
):
    if clinic_id:
        try:
            clinic_uuid = UUID(clinic_id)
            doctors = await DoctorService.get_all_doctors(db, clinic_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid clinic ID format")
    else:
        doctors = await DoctorService.get_all_doctors(db)
    
    # Include user information in response
    result_doctors = []
    for doctor in doctors:
        # Get user information
        user_result = await db.execute(select(User).where(User.id == doctor.user_id))
        doctor_user = user_result.scalar_one_or_none()
        
        doctor_dict = {
            "id": doctor.id,
            "user_id": doctor.user_id,
            "clinic_id": doctor.clinic_id,
            "specialty": doctor.specialty,
            "license_number": doctor.license_number,
            "years_experience": doctor.years_experience,
            "rating": doctor.rating,
            "is_available": doctor.is_available,
            "user": {
                "id": doctor_user.id,
                "first_name": doctor_user.first_name,
                "last_name": doctor_user.last_name,
                "email": doctor_user.email,
                "role": doctor_user.role
            } if doctor_user else None
        }
        result_doctors.append(DoctorResponse(**doctor_dict))
    
    return result_doctors

@router.post("/", response_model=DoctorResponse)
async def create_doctor(
    doctor_in: DoctorCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    doctor = await DoctorService.create_doctor(db, doctor_in)
    
    # Include user information in response
    user_result = await db.execute(select(User).where(User.id == doctor.user_id))
    doctor_user = user_result.scalar_one_or_none()
    
    doctor_dict = {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "clinic_id": doctor.clinic_id,
        "specialty": doctor.specialty,
        "license_number": doctor.license_number,
        "years_experience": doctor.years_experience,
        "rating": doctor.rating,
        "is_available": doctor.is_available,
        "user": {
            "id": doctor_user.id,
            "first_name": doctor_user.first_name,
            "last_name": doctor_user.last_name,
            "email": doctor_user.email,
            "role": doctor_user.role
        } if doctor_user else None
    }
    return DoctorResponse(**doctor_dict)

@router.get("/{id}", response_model=DoctorResponse)
async def get_doctor(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        doctor_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    
    doctor = await DoctorService.get_doctor_by_id(db, doctor_uuid)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Include user information
    user_result = await db.execute(select(User).where(User.id == doctor.user_id))
    doctor_user = user_result.scalar_one_or_none()
    
    doctor_dict = {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "clinic_id": doctor.clinic_id,
        "specialty": doctor.specialty,
        "license_number": doctor.license_number,
        "years_experience": doctor.years_experience,
        "rating": doctor.rating,
        "is_available": doctor.is_available,
        "user": {
            "id": doctor_user.id,
            "first_name": doctor_user.first_name,
            "last_name": doctor_user.last_name,
            "email": doctor_user.email,
            "role": doctor_user.role
        } if doctor_user else None
    }
    return DoctorResponse(**doctor_dict)

@router.put("/{id}", response_model=DoctorResponse)
async def update_doctor(
    id: str,
    doctor_in: DoctorUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "doctor"])) # or check own id
):
    try:
        doctor_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    
    # Check if user is doctor and trying to update their own profile
    if user.role == "doctor" and str(user.id) != id:
        # Get doctor by user_id to check if this is their own profile
        doctor_profile = await DoctorService.get_doctor_by_user_id(db, user.id)
        if not doctor_profile or str(doctor_profile.id) != id:
            raise HTTPException(status_code=403, detail="Not authorized to update this doctor")
    
    doctor = await DoctorService.update_doctor(db, doctor_uuid, doctor_in)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Include user information
    user_result = await db.execute(select(User).where(User.id == doctor.user_id))
    doctor_user = user_result.scalar_one_or_none()
    
    doctor_dict = {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "clinic_id": doctor.clinic_id,
        "specialty": doctor.specialty,
        "license_number": doctor.license_number,
        "years_experience": doctor.years_experience,
        "rating": doctor.rating,
        "is_available": doctor.is_available,
        "user": {
            "id": doctor_user.id,
            "first_name": doctor_user.first_name,
            "last_name": doctor_user.last_name,
            "email": doctor_user.email,
            "role": doctor_user.role
        } if doctor_user else None
    }
    return DoctorResponse(**doctor_dict)

@router.delete("/{id}")
async def delete_doctor(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    try:
        doctor_uuid = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    
    success = await DoctorService.delete_doctor(db, doctor_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {"status": "ok", "message": "Doctor deleted successfully"}

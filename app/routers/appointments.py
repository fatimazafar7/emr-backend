from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.appointment import AppointmentResponse, AppointmentCreate, AppointmentUpdate
from app.models.appointment import Appointment, AppointmentStatus
from app.dependencies import get_current_user, require_role

router = APIRouter()

from app.services.patient_service import PatientService

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    # Filter appointments based on user role
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        result = await db.execute(select(Appointment).where(Appointment.patient_id == patient.id))
    elif user.role == "doctor":
        # Doctors see appointments assigned to them (need to check if doctor model exists for user)
        from app.models.doctor import Doctor
        doctor_result = await db.execute(select(Doctor).where(Doctor.user_id == user.id))
        doctor = doctor_result.scalar_one_or_none()
        if doctor:
            result = await db.execute(select(Appointment).where(Appointment.doctor_id == doctor.id))
        else:
            result = await db.execute(select(Appointment)) # Fallback if doctor profile missing
    else:
        # Admins and nurses see all
        result = await db.execute(select(Appointment))
        
    return result.scalars().all()

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    appointment_data = appointment_in.dict()
    
    # If the user is a patient, ensure they are booking for themselves
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        # Always use the current patient's record ID, ignoring what the frontend might have sent
        appointment_data["patient_id"] = patient.id
    else:
        # For non-patients, if patient_id was a user_id, resolve it
        try:
            p_uuid = UUID(str(appointment_data["patient_id"]))
            patient = await PatientService.get_patient_by_user_id(db, p_uuid)
            if patient:
                appointment_data["patient_id"] = patient.id
        except:
            pass

    appointment = Appointment(**appointment_data)
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment

@router.get("/{id}", response_model=AppointmentResponse)
async def get_appointment(
    id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Appointment).where(Appointment.id == id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt

@router.patch("/{id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    id: str,
    status: AppointmentStatus,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Appointment).where(Appointment.id == id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = status
    await db.commit()
    await db.refresh(appointment)
    return appointment

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.appointment import AppointmentType, AppointmentStatus

class AppointmentBase(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    clinic_id: UUID
    scheduled_at: datetime
    duration_minutes: Optional[int] = 30
    type: Optional[AppointmentType] = AppointmentType.checkup
    status: Optional[AppointmentStatus] = AppointmentStatus.scheduled
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: UUID
    created_at: datetime
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True


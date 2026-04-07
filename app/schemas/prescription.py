from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PrescriptionBase(BaseModel):
    patient_id: UUID
    doctor_id: Optional[UUID] = None
    prescribing_doctor: Optional[str] = None
    appointment_id: Optional[UUID] = None
    medication_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    instructions: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionUpdate(BaseModel):
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    instructions: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None

class PrescriptionResponse(PrescriptionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

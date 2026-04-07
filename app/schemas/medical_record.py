from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class MedicalRecordBase(BaseModel):
    patient_name: Optional[str] = None
    patient_id: Optional[UUID] = None
    doctor_name: Optional[str] = None
    doctor_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    record_type: Optional[str] = None
    record_title: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    visit_date: Optional[str] = None
    created_by: Optional[str] = None  # "patient", "doctor", "admin"

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    record_type: Optional[str] = None
    record_title: Optional[str] = None
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None

class MedicalRecordResponse(MedicalRecordBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

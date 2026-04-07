from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.patient import Gender, BloodType

class UserInfo(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str

class PatientBase(BaseModel):
    user_id: UUID
    clinic_id: UUID
    date_of_birth: Optional[str] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    date_of_birth: Optional[str] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientResponse(PatientBase):
    id: UUID
    user: Optional[UserInfo] = None

    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    patients: List[PatientResponse]
    total: int
    page: int
    per_page: int

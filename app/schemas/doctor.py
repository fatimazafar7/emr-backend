from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UserInfo(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: str

class DoctorBase(BaseModel):
    user_id: UUID
    clinic_id: UUID
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    years_experience: Optional[str] = None
    rating: Optional[float] = 5.0
    is_available: Optional[bool] = True

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    years_experience: Optional[str] = None
    rating: Optional[float] = None
    is_available: Optional[bool] = None

class DoctorResponse(DoctorBase):
    id: UUID
    user: Optional[UserInfo] = None

    class Config:
        from_attributes = True

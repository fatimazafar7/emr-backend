from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import Optional, List, Any
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    clinic_id: UUID4

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserOut(UserBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# Clinic Schemas
class ClinicBase(BaseModel):
    name: str
    location: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None

class ClinicOut(ClinicBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# Patient Schemas
class PatientBase(BaseModel):
    name: str
    dob: Optional[str] = None
    age: Optional[float] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = []
    medical_history: Optional[List[dict]] = []
    status: str = "Active"

class PatientCreate(PatientBase):
    clinic_id: UUID4

class PatientOut(PatientBase):
    id: UUID4
    clinic_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

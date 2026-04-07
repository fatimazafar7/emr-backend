from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class VitalBase(BaseModel):
    patient_id: UUID
    recorded_by: UUID
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_oxygen: Optional[float] = None
    blood_sugar: Optional[float] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None

class VitalCreate(VitalBase):
    pass

class VitalUpdate(BaseModel):
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_oxygen: Optional[float] = None
    blood_sugar: Optional[float] = None
    notes: Optional[str] = None

class VitalResponse(VitalBase):
    id: UUID
    recorded_at: datetime

    class Config:
        from_attributes = True

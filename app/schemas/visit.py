from pydantic import BaseModel
from datetime import date
from typing import Optional
from uuid import UUID

class VisitBase(BaseModel):
    visit_date: date
    doctor_name: str
    subjective: str  # Patient's reported symptoms
    objective: str  # Observations/exam findings
    assessment: str  # Doctor's assessment
    plan: str  # Treatment plan
    follow_up_date: Optional[date] = None

class VisitCreate(VisitBase):
    patient_id: UUID

class VisitUpdate(BaseModel):
    visit_date: Optional[date] = None
    doctor_name: Optional[str] = None
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    follow_up_date: Optional[date] = None

class VisitResponse(VisitBase):
    id: UUID
    patient_id: UUID
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True

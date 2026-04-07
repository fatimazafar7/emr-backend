from pydantic import BaseModel
from datetime import date
from typing import Optional
from uuid import UUID

class DiagnosisBase(BaseModel):
    diagnosis_name: str
    icd_code: Optional[str] = None
    diagnosed_by: Optional[str] = None
    diagnosis_date: date
    severity: str  # Mild, Moderate, Severe
    status: str  # Active, Resolved, Chronic
    notes: Optional[str] = None

class DiagnosisCreate(DiagnosisBase):
    patient_id: UUID

class DiagnosisUpdate(BaseModel):
    diagnosis_name: Optional[str] = None
    icd_code: Optional[str] = None
    diagnosed_by: Optional[str] = None
    diagnosis_date: Optional[date] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class DiagnosisResponse(DiagnosisBase):
    id: UUID
    patient_id: UUID
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True

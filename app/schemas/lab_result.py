from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.lab_result import LabStatus, ResultStatus

class LabResultBase(BaseModel):
    patient_id: UUID
    doctor_id: Optional[UUID] = None
    test_name: str
    test_type: Optional[str] = None
    lab_name: Optional[str] = None
    test_date: Optional[datetime] = None
    result_value: Optional[str] = None
    unit: Optional[str] = None
    normal_range_min: Optional[float] = None
    normal_range_max: Optional[float] = None
    status: Optional[LabStatus] = LabStatus.pending
    result_status: Optional[ResultStatus] = ResultStatus.normal
    ordered_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = None
    ai_interpretation: Optional[str] = None

class LabResultCreate(LabResultBase):
    pass

class LabResultUpdate(BaseModel):
    result_value: Optional[str] = None
    status: Optional[LabStatus] = None
    result_status: Optional[ResultStatus] = None
    received_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = None
    ai_interpretation: Optional[str] = None

class LabResultResponse(LabResultBase):
    id: UUID

    class Config:
        from_attributes = True

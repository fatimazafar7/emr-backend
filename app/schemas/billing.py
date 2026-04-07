from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from app.models.billing import BillingStatus

class BillingBase(BaseModel):
    patient_id: UUID
    clinic_id: UUID
    appointment_id: Optional[UUID] = None
    services: Optional[List[Any]] = None
    subtotal: Optional[float] = 0.0
    insurance_coverage: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    status: Optional[BillingStatus] = BillingStatus.pending
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None

class BillingCreate(BillingBase):
    pass

class BillingUpdate(BaseModel):
    services: Optional[List[Any]] = None
    subtotal: Optional[float] = None
    insurance_coverage: Optional[float] = None
    total_amount: Optional[float] = None
    status: Optional[BillingStatus] = None
    paid_at: Optional[datetime] = None

class BillingResponse(BillingBase):
    id: UUID
    invoice_number: str
    created_at: datetime

    class Config:
        from_attributes = True

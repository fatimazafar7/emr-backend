import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import enum
from app.database import Base

class BillingStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"

class Billing(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    invoice_number = Column(String, unique=True, nullable=False, default=lambda: f"INV-{uuid.uuid4().hex[:8].upper()}")
    services = Column(JSON)  # Array of dicts
    subtotal = Column(Float, default=0.0)
    insurance_coverage = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(BillingStatus), default=BillingStatus.pending)
    due_date = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

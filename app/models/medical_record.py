import uuid
from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.database import Base

class MedicalRecord(Base):
    __tablename__ = "medicalrecords"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_name = Column(String(255), nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    record_title = Column(String(255), nullable=True)
    doctor_name = Column(String(255), nullable=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    record_type = Column(String)
    chief_complaint = Column(Text)
    symptoms = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    visit_date = Column(String, nullable=True)
    created_by = Column(String(50), nullable=True)  # "patient", "doctor", "admin"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

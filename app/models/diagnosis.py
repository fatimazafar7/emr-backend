import uuid
from sqlalchemy import Column, String, Date, Text, ForeignKey
from datetime import date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    diagnosis_name = Column(String, nullable=False)
    icd_code = Column(String, nullable=True)
    diagnosed_by = Column(String, nullable=True)
    diagnosis_date = Column(Date, nullable=False)
    severity = Column(String, nullable=False)  # Mild, Moderate, Severe
    status = Column(String, nullable=False)  # Active, Resolved, Chronic
    notes = Column(Text, nullable=True)
    created_at = Column(Date, nullable=False, default=date.today)
    updated_at = Column(Date, nullable=False, default=date.today, onupdate=date.today)
    
    # Relationships - use backref to avoid circular dependency
    patient = relationship("Patient", backref="diagnoses")

import uuid
from sqlalchemy import Column, String, Date, Text, ForeignKey
from datetime import date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    visit_date = Column(Date, nullable=False)
    doctor_name = Column(String, nullable=False)
    subjective = Column(Text, nullable=False)  # Patient's reported symptoms
    objective = Column(Text, nullable=False)  # Observations/exam findings
    assessment = Column(Text, nullable=False)  # Doctor's assessment
    plan = Column(Text, nullable=False)  # Treatment plan
    follow_up_date = Column(Date, nullable=True)
    created_at = Column(Date, nullable=False, default=date.today)
    updated_at = Column(Date, nullable=False, default=date.today, onupdate=date.today)
    
    # Relationships - use backref to avoid circular dependency
    patient = relationship("Patient", backref="visits")

import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import enum
from app.database import Base

class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class BloodType(str, enum.Enum):
    A_pos = "A+"
    A_neg = "A-"
    B_pos = "B+"
    B_neg = "B-"
    AB_pos = "AB+"
    AB_neg = "AB-"
    O_pos = "O+"
    O_neg = "O-"

class Patient(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=False)
    date_of_birth = Column(String)  # or date
    gender = Column(Enum(Gender))
    blood_type = Column(Enum(BloodType))
    allergies = Column(Text)
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    insurance_provider = Column(String)
    insurance_number = Column(String)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")


import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Text, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import enum
from app.database import Base

class LabStatus(str, enum.Enum):
    pending = "pending"
    received = "received"
    reviewed = "reviewed"

class ResultStatus(str, enum.Enum):
    normal = "normal"
    abnormal = "abnormal"
    critical = "critical"

class LabResult(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=True)
    test_name = Column(String, nullable=False)
    test_type = Column(String)
    lab_name = Column(String)
    test_date = Column(DateTime(timezone=True))
    result_value = Column(String)
    unit = Column(String)
    normal_range_min = Column(Float)
    normal_range_max = Column(Float)
    status = Column(Enum(LabStatus), default=LabStatus.pending)
    result_status = Column(Enum(ResultStatus), default=ResultStatus.normal)
    ordered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    received_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    ai_interpretation = Column(Text)

import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, JSON, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import enum
from app.database import Base

class AgentType(str, enum.Enum):
    diagnosis = "diagnosis"
    records = "records"
    prescription = "prescription"
    lab = "lab"
    billing = "billing"

class SessionStatus(str, enum.Enum):
    success = "success"
    error = "error"
    pending = "pending"

class AISession(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    agent_type = Column(Enum(AgentType), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    tokens_used = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    status = Column(Enum(SessionStatus), default=SessionStatus.pending)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

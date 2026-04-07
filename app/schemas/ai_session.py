from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from app.models.ai_session import AgentType, SessionStatus

class AISessionBase(BaseModel):
    doctor_id: UUID
    patient_id: Optional[UUID] = None
    agent_type: AgentType
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    tokens_used: Optional[int] = 0
    duration_ms: Optional[int] = 0
    status: Optional[SessionStatus] = SessionStatus.pending
    error_message: Optional[str] = None

class AISessionCreate(AISessionBase):
    pass

class AISessionUpdate(BaseModel):
    output_data: Optional[Any] = None
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None
    status: Optional[SessionStatus] = None
    error_message: Optional[str] = None

class AISessionResponse(AISessionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

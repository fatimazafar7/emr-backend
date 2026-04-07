from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.services.ai_service import AIService
from app.models.ai_session import AISession

router = APIRouter()
ai_service = AIService()

class DiagnosisRequest(BaseModel):
    patient_id: UUID
    symptoms: List[str]
    duration: str
    history: List[str]

class RecordsSummaryRequest(BaseModel):
    patient_id: UUID

class PrescriptionCheckRequest(BaseModel):
    patient_id: UUID
    medication: str
    dosage: str
    frequency: str

class LabInterpretRequest(BaseModel):
    lab_result_id: UUID

class GenerateBillRequest(BaseModel):
    appointment_id: UUID

@router.post("/diagnosis")
async def ai_diagnosis(
    req: DiagnosisRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor"]))
):
    try:
        return await ai_service.run_diagnosis(req.patient_id, user.id, req.symptoms, req.duration, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/records-summary")
async def ai_records_summary(
    req: RecordsSummaryRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "patient"]))
):
    # If patient, verify ownership
    if user.role == "patient":
        from app.services.patient_service import PatientService
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        if patient.id != req.patient_id:
            raise HTTPException(status_code=403, detail="You can only summarize your own records")
            
    try:
        return await ai_service.run_records_summary(req.patient_id, user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prescription-check")
async def ai_prescription_check(
    req: PrescriptionCheckRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "patient"]))
):
    # If patient, verify ownership
    if user.role == "patient":
        from app.services.patient_service import PatientService
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        if patient.id != req.patient_id:
            raise HTTPException(status_code=403, detail="You can only check your own prescriptions")

    try:
        return await ai_service.run_prescription_check(req.patient_id, user.id, req.medication, req.dosage, req.frequency, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lab-interpret")
async def ai_lab_interpret(
    req: LabInterpretRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin", "patient"]))
):
    # If patient, verify ownership
    if user.role == "patient":
        from app.models.lab_result import LabResult
        from app.services.patient_service import PatientService
        lab_res = await db.execute(select(LabResult).where(LabResult.id == req.lab_result_id))
        lab = lab_res.scalar_one_or_none()
        if not lab:
            raise HTTPException(status_code=404, detail="Lab result not found")
        
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        if lab.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="You can only interpret your own lab results")

    try:
        return await ai_service.run_lab_interpretation(req.lab_result_id, user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-bill")
async def ai_generate_bill(
    req: GenerateBillRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    try:
        return await ai_service.run_billing(req.appointment_id, user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def ai_stats(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    return await ai_service.get_agent_stats(db)

@router.get("/sessions")
async def ai_sessions(
    agent_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    query = select(AISession)
    if agent_type:
        query = query.where(AISession.agent_type == agent_type)
    if date_from:
        query = query.where(AISession.created_at >= date_from)
    if date_to:
        query = query.where(AISession.created_at <= date_to)
        
    result = await db.execute(query.order_by(AISession.created_at.desc()).limit(50))
    # Safe return using pure dicts mapped
    return result.scalars().all()

@router.get("/sessions/{id}")
async def ai_session_detail(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["doctor", "admin"]))
):
    result = await db.execute(select(AISession).where(AISession.id == id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="AI Session not found")
    return session

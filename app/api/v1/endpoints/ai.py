from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Any, List, Dict
from app.services.diagnosis_agent import DiagnosisAgent
from app.services.records_agent import RecordsAgent
from app.services.prescription_agent import PrescriptionAgent
from app.services.labs_agent import LabsAgent
from app.services.billing_agent import BillingAgent
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import AIJob
import uuid

router = APIRouter()

# Initialize Agents
diagnosis_agent = DiagnosisAgent()
records_agent = RecordsAgent()
prescription_agent = PrescriptionAgent()
labs_agent = LabsAgent()
billing_agent = BillingAgent()

@router.post("/diagnosis", response_model=Dict[str, Any])
async def trigger_diagnosis(
    symptoms: str = Body(...),
    history: List[Dict[str, Any]] = Body([]),
    db: AsyncSession = Depends(get_db)
):
    result = await diagnosis_agent.analyze_symptoms(symptoms, history)
    # Log job for Admin Monitor
    job = AIJob(
        clinic_id=uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"), # Mock clinic id for now
        agent_type="diagnosis",
        status="completed" if "data" in result else "failed",
        payload={"symptoms": symptoms},
        result=result.get("data"),
        latency_ms=result.get("latency_ms"),
        cost_tokens=result.get("usage", {}).get("total_tokens", 0)
    )
    db.add(job)
    await db.commit()
    return result

@router.post("/records/summary", response_model=Dict[str, Any])
async def trigger_records_summary(
    history: List[Dict[str, Any]] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    result = await records_agent.summarize_history(history)
    return result

@router.post("/prescription/check", response_model=Dict[str, Any])
async def trigger_prescription_check(
    new_med: str = Body(...),
    current_meds: List[str] = Body([]),
    allergies: List[str] = Body([]),
    db: AsyncSession = Depends(get_db)
):
    result = await prescription_agent.check_interaction(new_med, current_meds, allergies)
    return result

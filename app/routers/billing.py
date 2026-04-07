from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.schemas.billing import BillingResponse, BillingCreate, BillingUpdate
from app.models.billing import Billing
from app.dependencies import get_current_user, require_role

router = APIRouter()

from app.services.patient_service import PatientService

@router.get("/", response_model=List[BillingResponse])
async def get_billings(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "receptionist", "patient"]))
):
    # Filter billings based on user role
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        result = await db.execute(
            select(Billing).where(Billing.patient_id == patient.id)
        )
    else:
        # Admins and receptionists can see all billings
        result = await db.execute(select(Billing))
        
    return result.scalars().all()

@router.get("/{id}", response_model=BillingResponse)
async def get_billing(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Billing).where(Billing.id == id))
    billing = result.scalar_one_or_none()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing

@router.post("/", response_model=BillingResponse, status_code=status.HTTP_201_CREATED)
async def create_billing(
    billing_in: BillingCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "receptionist", "patient"]))
):
    billing_data = billing_in.dict()
    
    # If user is patient, force patient_id and clinic_id
    if user.role == "patient":
        patient = await PatientService.get_or_create_patient_by_user_id(db, user.id, user.clinic_id)
        billing_data["patient_id"] = patient.id
        # Use user's clinic_id or patient's clinic_id
        billing_data["clinic_id"] = patient.clinic_id
    else:
        # Ensure clinic_id is present if creating for a doctor/admin
        if not billing_data.get("clinic_id"):
            billing_data["clinic_id"] = user.clinic_id or UUID("12a681ac-a370-487a-b3ee-3f381d361064")
            
    billing = Billing(**billing_data)
    db.add(billing)
    await db.commit()
    await db.refresh(billing)
    return billing

@router.put("/{id}", response_model=BillingResponse)
async def update_billing(
    id: UUID,
    billing_in: BillingUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "receptionist"]))
):
    result = await db.execute(select(Billing).where(Billing.id == id))
    billing = result.scalar_one_or_none()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    for key, value in billing_in.dict(exclude_unset=True).items():
        setattr(billing, key, value)
    
    await db.commit()
    await db.refresh(billing)
    return billing

@router.patch("/{id}/status")
async def update_billing_status(
    id: UUID,
    payment_status: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin", "receptionist"]))
):
    result = await db.execute(select(Billing).where(Billing.id == id))
    billing = result.scalar_one_or_none()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    billing.status = payment_status
    if payment_status.lower() == "paid":
        billing.paid_at = datetime.now()
        
    await db.commit()
    return {"status": "ok", "message": "Billing status updated"}

@router.get("/stats/summary")
async def get_billing_summary(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_role(["admin"]))
):
    # Just a placeholder summary logic
    result = await db.execute(select(func.sum(Billing.total_amount)))
    total = result.scalar() or 0.0
    return {"total_revenue": total}

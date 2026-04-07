import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.lab_result import LabResult
from app.models.medical_record import MedicalRecord
from app.models.vital import Vital
from app.models.ai_session import AISession
from app.models.doctor import Doctor

from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.records_agent import RecordsSummaryAgent
from app.agents.prescription_agent import PrescriptionAgent
from app.agents.lab_agent import LabResultsAgent
from app.agents.billing_agent import BillingAgent

class AIService:
    def __init__(self):
        self.diagnosis_agent = DiagnosisAgent()
        self.records_agent = RecordsSummaryAgent()
        self.prescription_agent = PrescriptionAgent()
        self.lab_agent = LabResultsAgent()
        self.billing_agent = BillingAgent()

    async def _resolve_doctor_id(self, user_id: uuid.UUID, db: AsyncSession) -> uuid.UUID:
        result = await db.execute(select(Doctor).where(Doctor.user_id == user_id))
        doctor = result.scalar_one_or_none()
        if not doctor:
            # Fallback for admin or seeding
            res = await db.execute(select(Doctor).limit(1))
            doctor = res.scalar_one_or_none()
            if not doctor:
                raise ValueError("No doctor found in system to associate with AI session")
        return doctor.id

    async def run_diagnosis(self, patient_id: uuid.UUID, user_id: uuid.UUID, symptoms: List[str], duration: str, db: AsyncSession) -> Dict[str, Any]:
        doctor_id = await self._resolve_doctor_id(user_id, db)
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise ValueError("Patient not found")

        meds_res = await db.execute(select(Prescription).where(Prescription.patient_id == patient_id))
        meds = [m.medication_name for m in meds_res.scalars().all()]

        vitals_res = await db.execute(select(Vital).where(Vital.patient_id == patient_id).order_by(Vital.recorded_at.desc()).limit(1))
        vital = vitals_res.scalar_one_or_none()
        vital_dict = {"bp": f"{vital.blood_pressure_systolic}/{vital.blood_pressure_diastolic}", "hr": vital.heart_rate} if vital else {}

        input_data = {
            "patient_age": 34, # Placeholder logic 
            "patient_gender": patient.gender.value if patient.gender else "unknown",
            "symptoms": symptoms,
            "symptom_duration": duration,
            "medical_history": [],
            "current_medications": meds,
            "vitals": vital_dict
        }

        return await self.diagnosis_agent.analyze(input_data, db, doctor_id, patient_id)

    async def run_records_summary(self, patient_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
        doctor_id = await self._resolve_doctor_id(user_id, db)
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise ValueError("Patient not found")

        input_data = {
            "patient_info": {"age": 34, "gender": patient.gender.value if patient.gender else "unknown", "blood_type": patient.blood_type.value if patient.blood_type else "unknown"},
            "medical_records": [], # Mocks query
            "prescriptions": [],
            "lab_results": [],
            "vitals_history": [],
            "allergies": []
        }

        return await self.records_agent.summarize(input_data, db, doctor_id, patient_id)

    async def run_prescription_check(self, patient_id: uuid.UUID, user_id: uuid.UUID, medication: str, dosage: str, frequency: str, db: AsyncSession) -> Dict[str, Any]:
        doctor_id = await self._resolve_doctor_id(user_id, db)
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        
        input_data = {
            "new_medication": medication,
            "new_dosage": dosage,
            "new_frequency": frequency,
            "patient_age": 34,
            "patient_weight_kg": 70.0,
            "patient_allergies": [],
            "current_medications": [],
            "medical_conditions": []
        }
        
        return await self.prescription_agent.check(input_data, db, doctor_id, patient_id)

    async def run_lab_interpretation(self, lab_result_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
        doctor_id = await self._resolve_doctor_id(user_id, db)
        result = await db.execute(select(LabResult).where(LabResult.id == lab_result_id))
        lab = result.scalar_one_or_none()
        if not lab:
            raise ValueError("Lab result not found")

        input_data = {
            "test_name": lab.test_name,
            "test_value": float(lab.result_value) if lab.result_value.replace('.','',1).isdigit() else 0.0,
            "unit": lab.unit or "",
            "normal_range_min": lab.normal_range_min or 0.0,
            "normal_range_max": lab.normal_range_max or 100.0,
            "patient_age": 34,
            "patient_gender": "unknown",
            "patient_conditions": [],
            "previous_results": []
        }

        agent_result = await self.lab_agent.interpret(input_data, db, doctor_id, lab.patient_id)
        if "plain_language_explanation" in agent_result:
            lab.ai_interpretation = agent_result["plain_language_explanation"].get("for_doctor", "")
            await db.commit()
            
        return agent_result

    async def run_billing(self, appointment_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        app = result.scalar_one_or_none()
        if not app:
            raise ValueError("Appointment not found")

        input_data = {
            "appointment_type": app.type.value if app.type else "general",
            "services_provided": [app.reason] if app.reason else [],
            "diagnosis_codes": [],
            "patient_insurance": "Standard",
            "patient_age": 34,
            "clinic_location": "Main",
            "doctor_specialty": "General"
        }

        # Passing resolved doctor_id for tracking
        doctor_id = await self._resolve_doctor_id(user_id, db)
        return await self.billing_agent.generate_bill(input_data, db, doctor_id, app.patient_id)

    async def get_agent_stats(self, db: AsyncSession) -> Dict[str, Any]:
        result = await db.execute(select(AISession))
        sessions = result.scalars().all()
        
        success_count = sum(1 for s in sessions if s.status.value == "success")
        total_duration = sum(s.duration_ms for s in sessions if s.duration_ms)
        
        return {
            "total_sessions": len(sessions),
            "success_rate": round(success_count / len(sessions) * 100, 2) if sessions else 100.0,
            "avg_response_time": round(total_duration / len(sessions)) if sessions else 0,
            "sessions_today": len(sessions)
        }

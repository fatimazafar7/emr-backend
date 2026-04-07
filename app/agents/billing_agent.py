from app.agents.base_agent import BaseAgent
from app.models.ai_session import AgentType
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json

class BillingAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(agent_type=AgentType.billing, model=model)
        self.system_prompt = (
            "You are a medical billing AI assistant. You "
            "analyze appointments and services provided to "
            "generate accurate billing codes, calculate costs, "
            "check insurance coverage, and flag billing issues.\n\n"
            "Output structured JSON:\n"
            "{\n"
            '  "cpt_codes": [\n'
            '    {\n'
            '      "code": "CPT code",\n'
            '      "description": "service description",\n'
            '      "fee": 150.00\n'
            '    }\n'
            '  ],\n'
            '  "icd_codes": ["diagnosis codes used"],\n'
            '  "subtotal": 250.00,\n'
            '  "insurance_coverage_estimate": {\n'
            '    "covered_percentage": 80,\n'
            '    "estimated_covered": 200.00,\n'
            '    "patient_responsibility": 50.00,\n'
            '    "notes": "coverage details"\n'
            '  },\n'
            '  "billing_flags": ["any issues or notes"],\n'
            '  "recommended_payment_plan": null,\n'
            '  "total_due": 50.00,\n'
            '  "summary": "billing summary"\n'
            "}"
        )

    async def generate_bill(
        self, 
        input_data: Dict[str, Any], 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Expected input_schema:
        - appointment_type: str
        - services_provided: list[str]
        - diagnosis_codes: list[str]
        - patient_insurance: str
        - patient_age: int
        - clinic_location: str
        - doctor_specialty: str
        """
        user_prompt = json.dumps(input_data, indent=2)
        return await self.run(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            db=db,
            doctor_id=doctor_id,
            patient_id=patient_id
        )

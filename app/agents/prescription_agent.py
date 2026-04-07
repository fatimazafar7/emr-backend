from app.agents.base_agent import BaseAgent
from app.models.ai_session import AgentType
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json

class PrescriptionAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(agent_type=AgentType.prescription, model=model)
        self.system_prompt = (
            "You are a clinical pharmacology AI assistant. "
            "You check drug interactions, verify dosages based "
            "on patient profile, and flag any prescription "
            "concerns. Always prioritize patient safety.\n\n"
            "Output structured JSON:\n"
            "{\n"
            '  "safety_status": "safe/caution/danger",\n'
            '  "interactions": [\n'
            '    {\n'
            '      "drug_a": "medication 1",\n'
            '      "drug_b": "medication 2",\n'
            '      "severity": "mild/moderate/severe",\n'
            '      "effect": "what happens",\n'
            '      "recommendation": "what to do"\n'
            '    }\n'
            '  ],\n'
            '  "dosage_assessment": {\n'
            '    "recommended_dose": "correct dose for patient",\n'
            '    "current_dose_status": "appropriate/too_high/too_low",\n'
            '    "adjustment_needed": true,\n'
            '    "adjustment_reason": "why"\n'
            '  },\n'
            '  "allergy_check": {\n'
            '    "allergy_conflict": true,\n'
            '    "details": "explanation if conflict"\n'
            '  },\n'
            '  "contraindications": ["list of contraindications"],\n'
            '  "monitoring_required": ["what to monitor"],\n'
            '  "alternative_medications": ["safer alternatives if needed"],\n'
            '  "approval": true,\n'
            '  "summary": "overall assessment"\n'
            "}"
        )

    async def check(
        self, 
        input_data: Dict[str, Any], 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Expected input_schema:
        - new_medication: str
        - new_dosage: str
        - new_frequency: str
        - patient_age: int
        - patient_weight_kg: float
        - patient_allergies: list[str]
        - current_medications: list[dict]
        - medical_conditions: list[str]
        - kidney_function: str (optional)
        - liver_function: str (optional)
        """
        user_prompt = json.dumps(input_data, indent=2)
        return await self.run(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            db=db,
            doctor_id=doctor_id,
            patient_id=patient_id
        )

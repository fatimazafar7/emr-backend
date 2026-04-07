from app.agents.base_agent import BaseAgent
from app.models.ai_session import AgentType
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json

class DiagnosisAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(agent_type=AgentType.diagnosis, model=model)
        self.system_prompt = (
            "You are an expert medical AI assistant helping "
            "doctors with clinical decision support. You analyze "
            "patient symptoms and provide possible diagnoses with "
            "confidence scores. Always remind that your output is "
            "for assistance only and final diagnosis must be made "
            "by a licensed physician.\n\n"
            "Output must be structured JSON:\n"
            "{\n"
            '  "possible_diagnoses": [\n'
            '    {\n'
            '      "name": "diagnosis name",\n'
            '      "confidence": 85,\n'
            '      "icd_code": "ICD-10 code",\n'
            '      "reasoning": "why this diagnosis"\n'
            '    }\n'
            '  ],\n'
            '  "recommended_tests": [\n'
            '    {\n'
            '      "test_name": "test",\n'
            '      "urgency": "immediate/routine/optional",\n'
            '      "reason": "why order this"\n'
            '    }\n'
            '  ],\n'
            '  "red_flags": ["list of warning signs to watch"],\n'
            '  "treatment_suggestions": [\n'
            '    {\n'
            '      "option": "treatment",\n'
            '      "notes": "details"\n'
            '    }\n'
            '  ],\n'
            '  "follow_up": "recommended follow up timeline",\n'
            '  "disclaimer": "AI assistance only message"\n'
            "}"
        )

    async def analyze(
        self, 
        input_data: Dict[str, Any], 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Expected input_schema:
        - patient_age: int
        - patient_gender: str
        - symptoms: list[str]
        - symptom_duration: str
        - medical_history: list[str]
        - current_medications: list[str]
        - vitals: dict (optional)
        """
        user_prompt = json.dumps(input_data, indent=2)
        return await self.run(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            db=db,
            doctor_id=doctor_id,
            patient_id=patient_id
        )

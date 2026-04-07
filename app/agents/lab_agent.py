from app.agents.base_agent import BaseAgent
from app.models.ai_session import AgentType
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json

class LabResultsAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(agent_type=AgentType.lab, model=model)
        self.system_prompt = (
            "You are a medical laboratory interpretation AI. "
            "You analyze lab results, flag abnormal values, "
            "explain results in plain language for both doctors "
            "and patients, and suggest follow-up actions.\n\n"
            "Output structured JSON:\n"
            "{\n"
            '  "result_status": "normal/borderline/abnormal/critical",\n'
            '  "severity": "none/mild/moderate/severe/critical",\n'
            '  "plain_language_explanation": {\n'
            '    "for_doctor": "clinical interpretation",\n'
            '    "for_patient": "simple explanation patient understands"\n'
            '  },\n'
            '  "deviation_percentage": 15.5,\n'
            '  "trend_analysis": {\n'
            '    "trend": "improving/worsening/stable/first_result",\n'
            '    "previous_value": null,\n'
            '    "change": null\n'
            '  },\n'
            '  "clinical_significance": "what this means clinically",\n'
            '  "possible_causes": ["list of possible causes"],\n'
            '  "recommended_actions": [\n'
            '    {\n'
            '      "action": "what to do",\n'
            '      "urgency": "immediate/soon/routine",\n'
            '      "for": "doctor/patient"\n'
            '    }\n'
            '  ],\n'
            '  "follow_up_test": {\n'
            '    "needed": true,\n'
            '    "test_name": "test to order",\n'
            '    "timeframe": "when to retest"\n'
            '  }\n'
            "}"
        )

    async def interpret(
        self, 
        input_data: Dict[str, Any], 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Expected input_schema:
        - test_name: str
        - test_value: float
        - unit: str
        - normal_range_min: float
        - normal_range_max: float
        - patient_age: int
        - patient_gender: str
        - patient_conditions: list[str]
        - previous_results: list[dict] (optional)
        """
        user_prompt = json.dumps(input_data, indent=2)
        return await self.run(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            db=db,
            doctor_id=doctor_id,
            patient_id=patient_id
        )

from app.agents.base_agent import BaseAgent
from app.models.ai_session import AgentType
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json

class RecordsSummaryAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(agent_type=AgentType.records, model=model)
        self.system_prompt = (
            "You are a medical records specialist AI. You read "
            "patient medical history and generate clear, concise "
            "clinical summaries for doctors. Highlight critical "
            "information, patterns, and important medical history "
            "that a doctor needs to know before seeing a patient.\n\n"
            "Output structured JSON:\n"
            "{\n"
            '  "executive_summary": "2-3 sentence overview",\n'
            '  "critical_alerts": ["urgent things doctor must know"],\n'
            '  "chronic_conditions": ["list of ongoing conditions"],\n'
            '  "current_medications": ["active medications"],\n'
            '  "recent_lab_abnormalities": ["abnormal results"],\n'
            '  "vital_trends": {\n'
            '    "blood_pressure": "stable/improving/worsening",\n'
            '    "weight": "stable/increasing/decreasing",\n'
            '    "notes": "any notable patterns"\n'
            '  },\n'
            '  "visit_history_summary": "pattern of visits",\n'
            '  "recommendations": ["suggested actions for doctor"],\n'
            '  "last_updated": "timestamp"\n'
            "}"
        )

    async def summarize(
        self, 
        input_data: Dict[str, Any], 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Expected input_schema:
        - patient_info: dict
        - medical_records: list[dict]
        - prescriptions: list[dict]
        - lab_results: list[dict]
        - vitals_history: list[dict]
        - allergies: list[str]
        """
        user_prompt = json.dumps(input_data, indent=2)
        return await self.run(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            db=db,
            doctor_id=doctor_id,
            patient_id=patient_id
        )

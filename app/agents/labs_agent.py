from app.services.base_agent import BaseAgent
from typing import List, Dict, Any
import json

class LabsAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="Laboratory Specialist")

    async def interpret_results(self, lab_text: str, normal_ranges: Dict[str, str]) -> Dict[str, Any]:
        system_prompt = """
        You are EMR AI Labs AI, a world-class clinical pathologist.
        Interpret laboratory results and identify anomalies:
        1. Identification of results outside reference ranges
        2. Potential clinical implications of abnormal results
        3. Trends across multiple tests
        4. Recommended follow-up tests

        Output format MUST be JSON:
        {
            "abnormal": [{"biomarker": "str", "value": "str", "range": "str", "severity": "low-high-critical", "implication": "str"}],
            "trends": [{"biomarker": "str", "evolution": "improving-stable-worsening", "note": "str"}],
            "follow_up": ["str"],
            "conclusion": "str"
        }
        """
        
        user_content = f"Results: {lab_text}\nRanges: {json.dumps(normal_ranges)}"
        
        result = await self.generate_response(system_prompt, user_content)
        
        if "content" in result:
             result["data"] = json.loads(result["content"])
        
        return result

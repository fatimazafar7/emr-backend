import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.base_agent import SessionStatus

@pytest.mark.asyncio
async def test_diagnosis_agent_success():
    # Setup mock data
    mock_input = {
        "patient_age": 30,
        "patient_gender": "male",
        "symptoms": ["headache", "fever"],
        "symptom_duration": "2 days",
        "medical_history": [],
        "current_medications": [],
        "vitals": {}
    }
    
    mock_response_content = '{"possible_diagnoses": [{"name": "flu", "confidence": 90, "icd_code": "J10", "reasoning": "temp"}], "recommended_tests": [], "red_flags": [], "treatment_suggestions": [], "follow_up": "3 days", "disclaimer": "AI"}'
    
    # Mocking OpenAI response
    mock_choice = MagicMock()
    mock_choice.message.content = mock_response_content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 150
    
    # Setup Agent
    agent = DiagnosisAgent()
    
    # Mock the client
    agent.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    # Mock the DB AsyncSession mapping
    mock_db = AsyncMock()
    
    doctor_id = uuid4()
    
    # Run the test
    result = await agent.analyze(mock_input, mock_db, doctor_id)
    
    assert "possible_diagnoses" in result
    assert result["possible_diagnoses"][0]["name"] == "flu"
    
    # Verify _log_session logic
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_diagnosis_agent_json_error_retry():
    agent = DiagnosisAgent()
    
    # Force JSON parsing error on string
    mock_choice_bad = MagicMock()
    mock_choice_bad.message.content = 'INVALID JSON FORMAT'
    mock_response_bad = MagicMock()
    mock_response_bad.choices = [mock_choice_bad]
    
    agent.client.chat.completions.create = AsyncMock(return_value=mock_response_bad)
    mock_db = AsyncMock()
    
    # Should retry internally, and return the handled error Dict finally
    result = await agent.analyze({"symptoms": ["pain"]}, mock_db, uuid4())
    
    assert "error" in result
    assert result["error"] is True
    assert agent.client.chat.completions.create.call_count == 3

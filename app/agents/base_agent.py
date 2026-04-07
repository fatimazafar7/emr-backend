import json
import time
from typing import Dict, Any, List, Optional
from uuid import UUID
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.ai_session import AISession, AgentType, SessionStatus
import asyncio

class BaseAgent:
    def __init__(self, agent_type: AgentType, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.agent_type = agent_type
        self.model = model

    def _build_messages(self, system: str, user: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

    async def _log_session(
        self, 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID], 
        input_data: Dict[str, Any], 
        output_data: Optional[Dict[str, Any]], 
        tokens_used: int, 
        duration_ms: int, 
        status: SessionStatus, 
        error_message: Optional[str] = None
    ) -> AISession:
        session = AISession(
            doctor_id=doctor_id,
            patient_id=patient_id,
            agent_type=self.agent_type,
            input_data=input_data,
            output_data=output_data,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        return {
            "error": True,
            "message": str(error)
        }

    async def run(
        self, 
        prompt: str, 
        system_prompt: str, 
        db: AsyncSession, 
        doctor_id: UUID, 
        patient_id: Optional[UUID] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        messages = self._build_messages(system_prompt, prompt)
        
        for attempt in range(retries):
            start_time = time.time()
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                duration_ms = int((time.time() - start_time) * 1000)
                tokens_used = response.usage.total_tokens
                
                parsed_output = json.loads(content)
                
                # Log success
                await self._log_session(
                    db=db,
                    doctor_id=doctor_id,
                    patient_id=patient_id,
                    input_data={"prompt": prompt},
                    output_data=parsed_output,
                    tokens_used=tokens_used,
                    duration_ms=duration_ms,
                    status=SessionStatus.success
                )
                return parsed_output

            except json.JSONDecodeError as e:
                # Triggers retry
                if attempt == retries - 1:
                    duration_ms = int((time.time() - start_time) * 1000)
                    error_resp = self._handle_error(e)
                    await self._log_session(
                        db=db, doctor_id=doctor_id, patient_id=patient_id,
                        input_data={"prompt": prompt}, output_data=error_resp,
                        tokens_used=0, duration_ms=duration_ms, status=SessionStatus.error, error_message="JSON Parsing Error"
                    )
                    return error_resp
            except Exception as e:
                if attempt == retries - 1:
                    duration_ms = int((time.time() - start_time) * 1000)
                    error_resp = self._handle_error(e)
                    await self._log_session(
                        db=db, doctor_id=doctor_id, patient_id=patient_id,
                        input_data={"prompt": prompt}, output_data=error_resp,
                        tokens_used=0, duration_ms=duration_ms, status=SessionStatus.error, error_message=str(e)
                    )
                    return error_resp
            await asyncio.sleep(1) # wait before retry

    async def run_with_tools(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        pass # Optional structure placeholder for later tools mapping

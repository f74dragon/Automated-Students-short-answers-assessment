# app/schemas/llm_response_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LLMResponseCreate(BaseModel):
    raw_response: str
    grade: float
    feedback: Optional[str] = None
    student_answer_id: int

class LLMResponseResponse(LLMResponseCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class LLMResponseListResponse(BaseModel):
    llm_responses: list[LLMResponseResponse]

class GradeRequest(BaseModel):
    student_answer_id: int

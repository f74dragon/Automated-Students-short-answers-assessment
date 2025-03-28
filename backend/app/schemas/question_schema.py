# app/schemas/question_schema.py
from pydantic import BaseModel
from typing import Optional, List

class QuestionCreate(BaseModel):
    text: str
    model_answer: str
    collection_id: int

class QuestionResponse(QuestionCreate):
    id: int

    class Config:
        from_attributes = True

class QuestionListResponse(BaseModel):
    questions: list[QuestionResponse]

class QuestionDeleteResponse(BaseModel):
    message: str

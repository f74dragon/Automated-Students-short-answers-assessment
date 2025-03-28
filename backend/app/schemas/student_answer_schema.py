# app/schemas/student_answer_schema.py
from pydantic import BaseModel
from typing import Optional, List

class StudentAnswerCreate(BaseModel):
    answer: str
    student_id: int
    question_id: int

class StudentAnswerResponse(StudentAnswerCreate):
    id: int

    class Config:
        from_attributes = True

class StudentAnswerListResponse(BaseModel):
    student_answers: list[StudentAnswerResponse]

class StudentAnswerDeleteResponse(BaseModel):
    message: str

from pydantic import BaseModel
from typing import List, Optional

class StudentAnswerCreate(BaseModel):
    student_id: int
    question_id: int
    answer_text: str

class StudentAnswerResponse(StudentAnswerCreate):
    id: int

    class Config:
        from_attributes = True

class StudentAnswerListResponse(BaseModel):
    answers: List[StudentAnswerResponse]

class StudentAnswerDeleteResponse(BaseModel):
    message: str

# For bulk creation/submission of multiple answers at once
class StudentAnswerBulkCreate(BaseModel):
    student_id: int
    answers: List[dict]  # List of {question_id, answer_text} pairs

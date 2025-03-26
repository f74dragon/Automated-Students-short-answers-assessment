from pydantic import BaseModel
from typing import List

class QuestionCreate(BaseModel):
    collection_id: int
    question_text: str
    example_answer: str

class QuestionResponse(QuestionCreate):
    id: int

    class Config:
        from_attributes = True 

class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]

class QuestionDeleteResponse(BaseModel):
    message: str

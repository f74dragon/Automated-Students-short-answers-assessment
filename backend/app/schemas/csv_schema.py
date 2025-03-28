# app/schemas/csv_schema.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class ErrorDetail(BaseModel):
    row: int
    error: str

class QuestionUploadResponse(BaseModel):
    total: int
    created: int
    updated: int
    errors: int
    error_details: List[ErrorDetail]

class AnswerUploadResponse(BaseModel):
    total: int
    students_created: int
    students_updated: int
    answers_created: int
    answers_updated: int
    errors: int
    error_details: List[ErrorDetail]

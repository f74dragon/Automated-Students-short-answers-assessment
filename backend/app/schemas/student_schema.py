# app/schemas/student_schema.py
from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    answer: str
    collection_id: int

class StudentResponse(StudentCreate):
    id: int

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    students: list[StudentResponse]

class StudentDeleteResponse(BaseModel):
    message: str
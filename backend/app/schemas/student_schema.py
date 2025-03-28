# app/schemas/student_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class StudentCreate(BaseModel):
    name: str
    pid: str
    collection_id: int

class StudentResponse(StudentCreate):
    id: int

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    students: List[StudentResponse]

class StudentDeleteResponse(BaseModel):
    message: str

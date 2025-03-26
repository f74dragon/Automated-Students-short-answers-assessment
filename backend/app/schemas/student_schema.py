from pydantic import BaseModel
from typing import List, Optional

class StudentCreate(BaseModel):
    school_id: int
    student_name: str

class StudentResponse(StudentCreate):
    id: int

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    students: List[StudentResponse]

class StudentDeleteResponse(BaseModel):
    message: str

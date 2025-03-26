from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentListResponse, StudentDeleteResponse
from app.schemas.student_answer_schema import (
    StudentAnswerCreate, StudentAnswerResponse, StudentAnswerListResponse, 
    StudentAnswerDeleteResponse, StudentAnswerBulkCreate
)

"""
API Endpoints for Student Operations
"""

router = APIRouter(prefix="/students", tags=["students"])

# Creates a student
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db=db, student=student)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get all students
@router.get("/", response_model=StudentListResponse)
def get_all_students(db: Session = Depends(get_db)):
    return crud.get_students(db=db)

# Get a specific student
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student(db=db, student_id=student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Update a student
@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_student(db=db, student_id=student_id, new_student=student)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Delete a student
@router.delete("/{student_id}", response_model=StudentDeleteResponse)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_student(db=db, student_id=student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Student Answers Endpoints

# Add an answer for a student
@router.post("/{student_id}/answers", response_model=StudentAnswerResponse)
def create_student_answer(student_id: int, answer: StudentAnswerCreate, db: Session = Depends(get_db)):
    if answer.student_id != student_id:
        answer.student_id = student_id
    
    try:
        return crud.create_student_answer(db=db, answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Add multiple answers for a student in bulk
@router.post("/{student_id}/answers/bulk", response_model=StudentAnswerListResponse)
def create_student_answers_bulk(student_id: int, bulk_answers: StudentAnswerBulkCreate, db: Session = Depends(get_db)):
    if bulk_answers.student_id != student_id:
        bulk_answers.student_id = student_id
    
    try:
        return crud.create_student_answers_bulk(db=db, bulk_answers=bulk_answers)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get all answers for a student
@router.get("/{student_id}/answers", response_model=StudentAnswerListResponse)
def get_student_answers(student_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student_answers(db=db, student_id=student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get a specific answer
@router.get("/answers/{answer_id}", response_model=StudentAnswerResponse)
def get_student_answer(answer_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student_answer(db=db, answer_id=answer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Update a specific answer
@router.patch("/answers/{answer_id}", response_model=StudentAnswerResponse)
def update_student_answer(answer_id: int, answer: StudentAnswerCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_student_answer(db=db, answer_id=answer_id, new_answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Delete a specific answer
@router.delete("/answers/{answer_id}", response_model=StudentAnswerDeleteResponse)
def delete_student_answer(answer_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_student_answer(db=db, answer_id=answer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

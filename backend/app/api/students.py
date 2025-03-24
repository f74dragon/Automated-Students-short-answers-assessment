# app/api/students.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentListResponse, StudentDeleteResponse

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db=db, student=student)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/collection/{collection_id}", response_model=StudentListResponse)
def get_students_by_collection(collection_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_students_by_collection(db=db, collection_id=collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student(db=db, student_id=student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{student_id}", response_model=StudentDeleteResponse)
def remove_student(student_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_student(db=db, student_id=student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_student(db=db, student_id=student_id, student_update=student)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
# app/api/questions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.question_schema import QuestionCreate, QuestionResponse, QuestionListResponse, QuestionDeleteResponse

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_question(db=db, question=question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/collection/{collection_id}", response_model=QuestionListResponse)
def get_questions_by_collection(collection_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_questions_by_collection(db=db, collection_id=collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_question(db=db, question_id=question_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{question_id}", response_model=QuestionDeleteResponse)
def remove_question(question_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_question(db=db, question_id=question_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_question(db=db, question_id=question_id, question_update=question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

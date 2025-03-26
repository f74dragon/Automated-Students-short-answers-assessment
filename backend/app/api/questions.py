from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.question_schema import QuestionCreate, QuestionResponse, QuestionListResponse, QuestionDeleteResponse

"""
API Endpoints for Question Operations
"""

router = APIRouter(prefix="/collections/{collection_id}/questions", tags=["questions"])

# Creates a question and inserts into db
@router.post("/", response_model=QuestionResponse)
def create_question(collection_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    # Ensure the collection_id in path matches the one in request body
    if question.collection_id != collection_id:
        question.collection_id = collection_id
    
    try:
        return crud.create_question(db=db, question=question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get all questions for a collection
@router.get("/", response_model=QuestionListResponse)
def get_questions(collection_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_questions(db=db, collection_id=collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get a specific question
@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(collection_id: int, question_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_question(db=db, collection_id=collection_id, question_id=question_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Update a question
@router.patch("/{question_id}", response_model=QuestionResponse)
def update_question(collection_id: int, question_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    # Ensure the collection_id in path matches the one in request body
    if question.collection_id != collection_id:
        question.collection_id = collection_id
        
    try:
        return crud.update_question(db=db, collection_id=collection_id, question_id=question_id, new_question=question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Delete a question
@router.delete("/{question_id}", response_model=QuestionDeleteResponse)
def delete_question(collection_id: int, question_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_question(db=db, collection_id=collection_id, question_id=question_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

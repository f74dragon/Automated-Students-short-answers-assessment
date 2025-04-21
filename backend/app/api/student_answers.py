# app/api/student_answers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio
from app.database.connection import get_db
from app.database import crud
from app.schemas.student_answer_schema import StudentAnswerCreate, StudentAnswerResponse, StudentAnswerListResponse, StudentAnswerDeleteResponse
from app.schemas.llm_response_schema import LLMResponseResponse, LLMResponseCreate
from app.services.ollama_service import OllamaService

router = APIRouter(prefix="/student-answers", tags=["student_answers"])

@router.post("/", response_model=StudentAnswerResponse)
def create_student_answer(student_answer: StudentAnswerCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student_answer(db=db, student_answer=student_answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/student/{student_id}", response_model=StudentAnswerListResponse)
def get_student_answers_by_student(student_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student_answers_by_student(db=db, student_id=student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/question/{question_id}", response_model=StudentAnswerListResponse)
def get_student_answers_by_question(question_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student_answers_by_question(db=db, question_id=question_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{student_answer_id}", response_model=StudentAnswerResponse)
def get_student_answer(student_answer_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_student_answer(db=db, student_answer_id=student_answer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{student_answer_id}", response_model=StudentAnswerDeleteResponse)
def remove_student_answer(student_answer_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_student_answer(db=db, student_answer_id=student_answer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{student_answer_id}", response_model=StudentAnswerResponse)
def update_student_answer(student_answer_id: int, student_answer: StudentAnswerCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_student_answer(db=db, student_answer_id=student_answer_id, student_answer_update=student_answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{student_answer_id}/grade", response_model=LLMResponseResponse)
async def grade_student_answer(student_answer_id: int, db: Session = Depends(get_db)):
    """
    Grade a student's answer using the Ollama LLM.
    
    Args:
        student_answer_id: ID of the student answer to grade
        
    Returns:
        The LLM response with the grade and feedback
    """
    try:
        # Get student answer
        student_answer = crud.get_student_answer(db=db, student_answer_id=student_answer_id)
        
        # Get question and student
        question = crud.get_question(db=db, question_id=student_answer.question_id)
        
        # Get the singleton instance of Ollama service
        ollama_service = await OllamaService.get_instance()
        
        # Ensure model is downloaded
        if not await ollama_service.check_model_exists():
            await ollama_service.download_model()
        
        # Create prompt
        prompt = ollama_service.create_grading_prompt(
            question=question.text,
            model_answer=question.model_answer,
            student_answer=student_answer.answer
        )
        
        # Generate response
        response_text = await ollama_service.generate_response(prompt)
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate LLM response")
        
        # Extract grade and feedback
        grade, confidence = ollama_service.extract_grade(response_text)
        feedback = ollama_service.extract_feedback(response_text)
        
        # Create LLM response record
        llm_response_create = LLMResponseCreate(
            raw_response=response_text,
            grade=grade,
            feedback=feedback,
            student_answer_id=student_answer_id
        )
        
        llm_response = crud.create_llm_response(db=db, llm_response=llm_response_create)
        
        return llm_response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grading error: {str(e)}")

@router.get("/{student_answer_id}/grades", response_model=LLMResponseResponse)
def get_latest_grade(student_answer_id: int, db: Session = Depends(get_db)):
    """
    Get the latest grade for a student answer.
    
    Args:
        student_answer_id: ID of the student answer
        
    Returns:
        The latest LLM response with grade and feedback
    """
    try:
        return crud.get_latest_llm_response_by_student_answer(db=db, student_answer_id=student_answer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

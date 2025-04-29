# app/api/student_answers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio
import logging
from app.database.connection import get_db
from app.database import crud
from app.schemas.student_answer_schema import StudentAnswerCreate, StudentAnswerResponse, StudentAnswerListResponse, StudentAnswerDeleteResponse
from app.schemas.llm_response_schema import LLMResponseResponse, LLMResponseCreate
from app.services.ollama_service import OllamaService
from app.models.collection import Collection
from app.models.combination import Combination

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
    logger = logging.getLogger(__name__)
    
    try:
        # Get student answer
        student_answer = crud.get_student_answer(db=db, student_answer_id=student_answer_id)
        
        # Get question and its associated collection
        question = crud.get_question(db=db, question_id=student_answer.question_id)
        collection = db.query(Collection).filter(Collection.id == question.collection_id).first()
        
        # Initialize variables for model and prompt
        model_name = None
        custom_prompt = None
        
        # Check if collection has an associated combination
        if collection and collection.combination_id:
            combination = db.query(Combination).filter(Combination.id == collection.combination_id).first()
            if combination:
                model_name = combination.model_name
                custom_prompt = combination.prompt
        
        # Initialize Ollama service with custom model (if available)
        ollama_service = OllamaService(model_name=model_name) if model_name else OllamaService()
        
        # Function to generate the response
        async def generate_and_process_response():
            # Create prompt - either use custom prompt or fall back to default
            if custom_prompt:
                # Replace placeholders in custom prompt with actual values
                prompt = custom_prompt.replace("{{question}}", question.text)
                prompt = prompt.replace("{{model_answer}}", question.model_answer)
                prompt = prompt.replace("{{student_answer}}", student_answer.answer)
            else:
                # Use the default prompt format
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
            
            return crud.create_llm_response(db=db, llm_response=llm_response_create)
        
        # First attempt - check if model exists and download if needed
        model_exists = await ollama_service.check_model_exists()
        if not model_exists:
            logger.info(f"Model {ollama_service.model_name} not found, attempting to download...")
            await ollama_service.download_model()
        
        try:
            # First attempt to generate response
            return await generate_and_process_response()
        except Exception as first_error:
            # If we get an error, specifically download the Gemma3:4b model
            logger.warning(f"Error during grading: {str(first_error)}. Attempting to download gemma3:4b model...")
            
            # Force download Gemma3:4b model (even if we were using a different model originally)
            gemma_service = OllamaService(model_name="gemma3:4b")
            download_success = await gemma_service.download_model()
            
            if download_success:
                logger.info("Successfully downloaded gemma3:4b model, retrying grading...")
                
                # If we were using a custom model but it failed, switch to gemma3:4b
                if ollama_service.model_name != "gemma3:4b":
                    logger.info(f"Switching from {ollama_service.model_name} to gemma3:4b for retry")
                    ollama_service.model_name = "gemma3:4b"
                
                # Retry with the downloaded model
                return await generate_and_process_response()
            else:
                # If download also failed, re-raise the original error
                logger.error("Failed to download gemma3:4b model, cannot proceed with grading")
                raise first_error
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unrecoverable error during grading: {str(e)}")
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

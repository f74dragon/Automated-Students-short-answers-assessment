# app/api/student_answers.py
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import json
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

@router.post("/{student_answer_id}/grade/stream")
async def stream_grade_download_progress(student_answer_id: int, db: Session = Depends(get_db)):
    """
    Stream the progress of model downloads during the grading process.
    
    Args:
        student_answer_id: ID of the student answer to grade
        
    Returns:
        Streaming response with download progress updates
    """
    logger = logging.getLogger(__name__)
    
    async def progress_stream():
        try:
            # Get student answer
            student_answer = crud.get_student_answer(db=db, student_answer_id=student_answer_id)
            
            # Get question and its associated collection
            question = crud.get_question(db=db, question_id=student_answer.question_id)
            collection = db.query(Collection).filter(Collection.id == question.collection_id).first()
            
            # Initialize variables for model and prompt
            model_name = None
            
            # Check if collection has an associated combination
            if collection and collection.combination_id:
                combination = db.query(Combination).filter(Combination.id == collection.combination_id).first()
                if combination:
                    model_name = combination.model_name
            
            # Initialize Ollama service with custom model (if available)
            ollama_service = OllamaService(model_name=model_name) if model_name else OllamaService()
            
            # First check if model exists
            exists = await ollama_service.check_model_exists()
            if exists:
                logger.info(f"Model '{ollama_service.model_name}' already exists")
                yield json.dumps({"status": "model_exists", "model_name": ollama_service.model_name}) + "\n"
                
                # Try generating response
                try:
                    # Create a basic prompt just to test
                    sample_prompt = "Hello, are you working?"
                    response_text = await ollama_service.generate_response(sample_prompt)
                    
                    if response_text:
                        # Model is working fine
                        yield json.dumps({"status": "model_ready", "model_name": ollama_service.model_name}) + "\n"
                    else:
                        # Model exists but might have issues
                        yield json.dumps({"status": "model_issue", "message": "Model exists but couldn't generate response"}) + "\n"
                        
                        # Try downloading gemma3:4b specifically
                        gemma_service = OllamaService(model_name="gemma3:4b")
                        yield json.dumps({"status": "downloading_gemma", "message": "Downloading gemma3:4b model"}) + "\n"
                        
                        async for progress in gemma_service.stream_download_progress("gemma3:4b"):
                            yield json.dumps(progress) + "\n"
                except Exception as e:
                    logger.error(f"Error testing model: {str(e)}")
                    yield json.dumps({"status": "error", "message": f"Error testing model: {str(e)}"}) + "\n"
                    
                    # Try downloading gemma3:4b specifically
                    gemma_service = OllamaService(model_name="gemma3:4b")
                    yield json.dumps({"status": "downloading_gemma", "message": "Downloading gemma3:4b model"}) + "\n"
                    
                    async for progress in gemma_service.stream_download_progress("gemma3:4b"):
                        yield json.dumps(progress) + "\n"
            else:
                logger.info(f"Model '{ollama_service.model_name}' does not exist, downloading...")
                yield json.dumps({"status": "model_not_found", "model_name": ollama_service.model_name}) + "\n"
                
                # Stream download progress
                async for progress in ollama_service.stream_download_progress():
                    # Add model name to the progress data
                    progress["model_name"] = ollama_service.model_name
                    yield json.dumps(progress) + "\n"
            
            # Final success message
            yield json.dumps({"status": "success", "message": "Model ready for grading"}) + "\n"
            
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            yield json.dumps({"status": "error", "message": f"Error: {str(e)}"}) + "\n"
    
    # Return a streaming response with the progress updates
    return StreamingResponse(
        progress_stream(),
        media_type="text/event-stream"
    )

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
    logger.info(f"Starting grading for student answer ID {student_answer_id}")
    
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
        logger.info(f"Using model: {ollama_service.model_name}")
        
        # Ensure model is downloaded - note that the UI should use the streaming endpoint to show progress
        if not await ollama_service.check_model_exists():
            logger.info(f"Model {ollama_service.model_name} not found, downloading...")
            await ollama_service.download_model()
        
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
        logger.info(f"Generating response for student answer ID {student_answer_id}")
        response_text = await ollama_service.generate_response(prompt)
        
        if not response_text:
            logger.error("Failed to generate LLM response")
            raise HTTPException(status_code=500, detail="Failed to generate LLM response")
        
        # Extract grade and feedback
        grade, confidence = ollama_service.extract_grade(response_text)
        feedback = ollama_service.extract_feedback(response_text)
        logger.info(f"Grade extracted: {grade}, confidence: {confidence}")
        
        # Create LLM response record
        llm_response_create = LLMResponseCreate(
            raw_response=response_text,
            grade=grade,
            feedback=feedback,
            student_answer_id=student_answer_id
        )
        
        llm_response = crud.create_llm_response(db=db, llm_response=llm_response_create)
        logger.info(f"Successfully graded student answer {student_answer_id}")
        
        return llm_response
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error during grading: {str(e)}")
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

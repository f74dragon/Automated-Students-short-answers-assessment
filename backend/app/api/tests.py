from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import json
import asyncio
import time
from datetime import datetime

from app.database.connection import get_db
from app.models.test import Test, TestResult, TestSummary
from app.models.prompt import Prompt
from app.schemas.test_schema import (
    TestCreate,
    TestConfig,
    TestUpload,
    TestResult as TestResultSchema,
    TestWithResults,
    TestStatus
)
from app.services.ollama_service import OllamaService
from app.auth.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/tests", tags=["tests"])
ollama_service = OllamaService()

@router.get("/", response_model=List[TestConfig])
async def get_tests(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all tests from the database."""
    tests = db.query(Test).order_by(Test.created_at.desc()).offset(skip).limit(limit).all()
    return tests

@router.post("/", response_model=TestConfig, status_code=status.HTTP_201_CREATED)
async def create_test(
    test: TestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create a new test configuration."""
    # Verify models exist in Ollama
    try:
        response = await ollama_service._make_request_with_retry("GET", "api/tags")
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch models from Ollama"
            )
        
        models = response.json().get("models", [])
        for model_name in test.model_names:
            model_exists = any(model["name"] == model_name for model in models)
            if not model_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model '{model_name}' not found in Ollama"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking models: {str(e)}"
        )
    
    # Verify prompts exist
    for prompt_id in test.prompt_ids:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prompt with ID {prompt_id} not found"
            )
    
    # Create the test
    db_test = Test(
        name=test.name,
        description=test.description,
        model_names=test.model_names,
        prompt_ids=test.prompt_ids,
        status=TestStatus.PENDING
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@router.get("/{test_id}", response_model=TestWithResults)
async def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get a specific test by ID with its results."""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    return test

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Delete a test."""
    db_test = db.query(Test).filter(Test.id == test_id).first()
    if not db_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    db.delete(db_test)
    db.commit()
    return None

@router.post("/{test_id}/upload")
async def upload_test_data(
    test_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Upload CSV data for a test and start processing."""
    # Check if test exists
    db_test = db.query(Test).filter(Test.id == test_id).first()
    if not db_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    # Check file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Read CSV content
    contents = await file.read()
    
    try:
        # Parse the CSV
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate CSV columns
        required_columns = ["Question", "Model Answer", "Student Answer", "Model Grade"]
        for column in required_columns:
            if column not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV must contain column: {column}"
                )
        
        # Update test status
        db_test.status = TestStatus.RUNNING
        db.commit()
        
        # Start processing in background
        background_tasks.add_task(
            process_test_data,
            test_id=test_id,
            df=df,
            model_names=db_test.model_names,
            prompt_ids=db_test.prompt_ids,
            db=db
        )
        
        return {"message": f"Test data uploaded and processing started for test ID {test_id}"}
    
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The CSV file is empty"
        )
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error parsing CSV file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )

async def process_test_data(test_id: int, df: pd.DataFrame, model_names: List[str], prompt_ids: List[int], db: Session):
    """Process test data with selected models and prompts."""
    try:
        # Fetch the test
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            print(f"Test {test_id} not found")
            return
        
        # Fetch prompts
        prompts = {}
        for prompt_id in prompt_ids:
            prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
            if prompt:
                prompts[prompt_id] = prompt.prompt
        
        for model_name in model_names:
            for prompt_id, prompt_template in prompts.items():
                await process_model_prompt_combination(
                    test_id=test_id,
                    model_name=model_name,
                    prompt_id=prompt_id,
                    prompt_template=prompt_template,
                    df=df,
                    db=db
                )
        
        # Update test status to completed
        test.status = TestStatus.COMPLETED
        db.commit()
    
    except Exception as e:
        print(f"Error processing test data: {str(e)}")
        
        # Update test status to failed
        test = db.query(Test).filter(Test.id == test_id).first()
        if test:
            test.status = TestStatus.FAILED
            db.commit()

async def process_model_prompt_combination(
    test_id: int, 
    model_name: str, 
    prompt_id: int, 
    prompt_template: str, 
    df: pd.DataFrame, 
    db: Session
):
    """Process test data for a specific model and prompt combination."""
    results = []
    total_accuracy = 0.0
    total_response_time = 0.0
    
    service = OllamaService(model_name=model_name)
    
    for _, row in df.iterrows():
        question = row["Question"]
        model_answer = row["Model Answer"]
        student_answer = row["Student Answer"]
        model_grade = float(row["Model Grade"])
        
        # Format prompt using template
        formatted_prompt = prompt_template.replace("{{question}}", question)
        formatted_prompt = formatted_prompt.replace("{{model_answer}}", model_answer)
        formatted_prompt = formatted_prompt.replace("{{student_answer}}", student_answer)
        
        start_time = time.time()
        response = await service.generate_response(formatted_prompt)
        response_time = time.time() - start_time
        
        # Extract grade from response
        extracted_grade, _ = service.extract_grade(response)
        
        # Calculate accuracy (simple 1 - absolute difference)
        accuracy = 1 - min(1.0, abs(extracted_grade - model_grade))
        
        # Store result
        result = TestResult(
            test_id=test_id,
            model_name=model_name,
            prompt_id=prompt_id,
            question=question,
            student_answer=student_answer,
            model_answer=model_answer,
            model_grade=model_grade,
            extracted_grade=extracted_grade,
            accuracy=accuracy,
            response_time=response_time,
            full_response=response
        )
        
        db.add(result)
        results.append(result)
        
        total_accuracy += accuracy
        total_response_time += response_time
    
    # Commit all results
    db.commit()
    
    # Create summary
    if results:
        average_accuracy = total_accuracy / len(results)
        average_response_time = total_response_time / len(results)
        
        summary = TestSummary(
            test_id=test_id,
            model_name=model_name,
            prompt_id=prompt_id,
            average_accuracy=average_accuracy,
            average_response_time=average_response_time,
            total_questions=len(results)
        )
        
        db.add(summary)
        db.commit()

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import csv
import io

from app.database.connection import get_db
from app.auth.auth import get_current_active_user, get_admin_user

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_csv_for_evaluation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can upload
):
    """
    Upload a CSV file with questions, model answers, and student answers for evaluation.
    
    The CSV should have at least the following columns:
    - Question
    - ModelAnswer
    - StudentAnswer
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Read the CSV file
        contents = await file.read()
        decoded_content = contents.decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(decoded_content))
        
        # Process the CSV data
        evaluation_questions = []
        
        # Get the first row to check column headers
        fieldnames = csv_data.fieldnames
        
        # Check for column names - support both with and without spaces
        question_column = "Question"
        model_answer_column = None
        student_answer_column = None
        reference_grade_column = None
        
        # Find appropriate column names
        for field in fieldnames:
            if field == "ModelAnswer" or field == "Model Answer":
                model_answer_column = field
            elif field == "StudentAnswer" or field == "Student Answer":
                student_answer_column = field
            elif field == "ReferenceGrade" or field == "Reference Grade" or field == "Model Grade":
                reference_grade_column = field
        
        # Verify required columns exist
        if not all([question_column, model_answer_column, student_answer_column]):
            missing_columns = []
            if not question_column:
                missing_columns.append("Question")
            if not model_answer_column:
                missing_columns.append("ModelAnswer/Model Answer")
            if not student_answer_column:
                missing_columns.append("StudentAnswer/Student Answer")
                
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns in CSV: {', '.join(missing_columns)}"
            )
        
        # Process rows
        for i, row in enumerate(csv_data):
            # Add the question data
            evaluation_questions.append({
                "id": i + 1,  # Generate temporary IDs for frontend use
                "text": row[question_column],
                "model_answer": row[model_answer_column],
                "student_answer": row[student_answer_column],
                # Include reference grade if available
                "reference_grade": row.get(reference_grade_column, None) if reference_grade_column else None
            })
        
        if not evaluation_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid questions found in the CSV file"
            )
        
        return {
            "questions": evaluation_questions,
            "count": len(evaluation_questions),
            "filename": file.filename
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {str(e)}"
        )

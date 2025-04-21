from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any

from app.database.connection import get_db
from app.models.evaluation import Evaluation, Combination
from app.models.prompt import Prompt
from app.models.model import Model
from app.models.question import Question
from app.models.student_answer import StudentAnswer
from app.schemas.evaluation_schema import (
    EvaluationCreate, EvaluationUpdate, Evaluation as EvaluationSchema,
    CombinationCreate, CombinationUpdate, Combination as CombinationSchema,
    CombinationWithEvaluations, EvaluationRequest, EvaluationResponse
)
from app.services.ollama_service import OllamaService
from app.auth.auth import get_current_active_user, get_admin_user

router = APIRouter()
ollama_service = OllamaService()

# Combinations endpoints

@router.get("/combinations", response_model=List[CombinationSchema])
async def get_combinations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all prompt-model combinations."""
    combinations = db.query(Combination).offset(skip).limit(limit).all()
    return combinations

@router.get("/combinations/active", response_model=CombinationSchema)
async def get_active_combination(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get the currently active combination."""
    combination = db.query(Combination).filter(Combination.is_active == True).first()
    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active combination found"
        )
    return combination

@router.get("/combinations/{combination_id}", response_model=CombinationWithEvaluations)
async def get_combination(
    combination_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific combination by ID with its evaluations."""
    combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    return combination

@router.post("/combinations", response_model=CombinationSchema, status_code=status.HTTP_201_CREATED)
async def create_combination(
    combination: CombinationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can create
):
    """Create a new prompt-model combination."""
    # Verify that prompt and model exist
    prompt = db.query(Prompt).filter(Prompt.id == combination.prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {combination.prompt_id} not found"
        )
    
    model = db.query(Model).filter(Model.id == combination.model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {combination.model_id} not found"
        )
    
    try:
        # Create combination with cached prompt and model data
        db_combination = Combination(
            **combination.dict(),
            prompt_template=prompt.template,
            model_name=model.name
        )
        db.add(db_combination)
        db.commit()
        db.refresh(db_combination)
        return db_combination
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating combination"
        )

@router.put("/combinations/{combination_id}", response_model=CombinationSchema)
async def update_combination(
    combination_id: int,
    combination_update: CombinationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can update
):
    """Update an existing combination."""
    db_combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not db_combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    update_data = combination_update.dict(exclude_unset=True)
    
    # If the prompt is being updated, cache the template
    if 'prompt_id' in update_data:
        prompt = db.query(Prompt).filter(Prompt.id == update_data['prompt_id']).first()
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt with ID {update_data['prompt_id']} not found"
            )
        update_data['prompt_template'] = prompt.template
    
    # If the model is being updated, cache the name
    if 'model_id' in update_data:
        model = db.query(Model).filter(Model.id == update_data['model_id']).first()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model with ID {update_data['model_id']} not found"
            )
        update_data['model_name'] = model.name
    
    # Handle activation explicitly
    if 'is_active' in update_data and update_data['is_active']:
        # Deactivate all combinations first
        db.query(Combination).update({Combination.is_active: False})
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_combination, field, value)
    
    try:
        db.commit()
        db.refresh(db_combination)
        
        # If this combination was activated, update the active model and prompt in the service
        if db_combination.is_active:
            ollama_service.set_model(db_combination.model_name)
            # If the model has parameters, set them
            model = db.query(Model).filter(Model.id == db_combination.model_id).first()
            if model and model.parameters:
                ollama_service.set_parameters(model.parameters)
        
        return db_combination
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating combination"
        )

@router.put("/combinations/{combination_id}/activate", response_model=CombinationSchema)
async def activate_combination(
    combination_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can activate
):
    """Set a combination as the active one."""
    # First, deactivate all combinations
    db.query(Combination).update({Combination.is_active: False})
    
    # Then activate the specified combination
    db_combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not db_combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    # Set the model and prompt as active too
    db.query(Model).update({Model.is_active: False})
    db.query(Prompt).update({Prompt.is_active: False})
    
    model = db.query(Model).filter(Model.id == db_combination.model_id).first()
    prompt = db.query(Prompt).filter(Prompt.id == db_combination.prompt_id).first()
    
    if model:
        model.is_active = True
        ollama_service.set_model(model.name)
        if model.parameters:
            ollama_service.set_parameters(model.parameters)
    
    if prompt:
        prompt.is_active = True
    
    db_combination.is_active = True
    db.commit()
    db.refresh(db_combination)
    return db_combination

@router.delete("/combinations/{combination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_combination(
    combination_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can delete
):
    """Delete a combination."""
    db_combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not db_combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    # Don't allow deleting the active combination
    if db_combination.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active combination. Please activate another one first."
        )
    
    db.delete(db_combination)
    db.commit()
    return None

# Evaluations endpoints

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_model_prompt(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can run evaluations
):
    """Evaluate a model and prompt combination on selected questions."""
    
    # Resolve prompt and model info
    prompt_template = request.prompt_template
    model_name = request.model_name
    
    if request.prompt_id:
        prompt = db.query(Prompt).filter(Prompt.id == request.prompt_id).first()
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt with ID {request.prompt_id} not found"
            )
        prompt_template = prompt.template
    
    if request.model_id:
        model = db.query(Model).filter(Model.id == request.model_id).first()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model with ID {request.model_id} not found"
            )
        model_name = model.name
    
    if not prompt_template or not model_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either prompt_id/prompt_template and model_id/model_name must be provided"
        )
    
    # Fetch questions to evaluate
    questions = []
    
    # Check if we're using CSV questions directly
    if hasattr(request, 'csv_questions') and request.csv_questions:
        # Use the CSV questions directly
        for q in request.csv_questions:
            questions.append({
                "id": q.get("id", 0),  # Use temp ID from CSV
                "text": q.get("text", ""),
                "model_answer": q.get("model_answer", ""),
                "student_answer": q.get("student_answer", ""),
                "student_answer_id": None,  # No DB ID for CSV questions
                "reference_grade": q.get("reference_grade")  # Include reference grade if available
            })
    # Otherwise, use question IDs from the database
    elif request.question_ids:
        for qid in request.question_ids:
            question = db.query(Question).filter(Question.id == qid).first()
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {qid} not found"
                )
            
            # Fetch a matching student answer if available
            student_answer = db.query(StudentAnswer).join(Question).filter(
                StudentAnswer.question_id == question.id
            ).first()
            
            # Skip if no student answer available
            if not student_answer:
                continue
            
            # Create question data for evaluation
            questions.append({
                "id": question.id,
                "text": question.text,
                "model_answer": question.model_answer,
                "student_answer": student_answer.answer,
                "student_answer_id": student_answer.id
            })
    else:
        # Get a sample of questions with student answers
        student_answers = db.query(StudentAnswer).join(Question).limit(5).all()
        for sa in student_answers:
            questions.append({
                "id": sa.question_id,
                "text": sa.question.text,
                "model_answer": sa.question.model_answer,
                "student_answer": sa.answer,
                "student_answer_id": sa.id
            })
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions with student answers found for evaluation"
        )
    
    # Run the evaluation
    evaluation_result = await ollama_service.evaluate_model_prompt(
        model_name=model_name,
        prompt_template=prompt_template,
        questions=questions,
        parameters=request.parameters
    )
    
    # Save results if requested
    combination_id = None
    if request.save_result:
        # Create or find model
        db_model = db.query(Model).filter(Model.name == model_name).first()
        if not db_model:
            db_model = Model(
                name=model_name,
                parameters=request.parameters
            )
            db.add(db_model)
            db.flush()
        
        # Create or find prompt
        prompt_name = request.combination_name or f"Prompt for {model_name}"
        db_prompt = db.query(Prompt).filter(Prompt.template == prompt_template).first()
        if not db_prompt:
            db_prompt = Prompt(
                name=prompt_name,
                template=prompt_template
            )
            db.add(db_prompt)
            db.flush()
        
        # Create combination
        db_combination = Combination(
            prompt_id=db_prompt.id,
            model_id=db_model.id,
            name=request.combination_name or f"{model_name} with {prompt_name}",
            parameters=request.parameters,
            prompt_template=prompt_template,
            model_name=model_name,
            average_accuracy=evaluation_result["metrics"].get("average_accuracy"),
            average_response_time=evaluation_result["metrics"].get("average_response_time")
        )
        db.add(db_combination)
        db.flush()
        combination_id = db_combination.id
        
        # Save individual evaluations
        for result in evaluation_result["results"]:
            if "error" in result and result["error"]:
                continue
                
            metrics = {
                "extracted_grade": result.get("extracted_grade"),
                "confidence": result.get("confidence"),
                "response_time": result.get("response_time", 0),
                "accuracy": result.get("accuracy", 0)
            }
            
            # Determine if we're using CSV questions (where we don't want to reference question_id)
            is_using_csv = hasattr(request, 'is_csv') and request.is_csv
            
            eval_data = {
                "prompt_id": db_prompt.id,
                "model_id": db_model.id,
                # Only include question_id and student_answer_id if not using CSV
                "question_id": None if is_using_csv else result.get("question_id"),
                "student_answer_id": None if is_using_csv else result.get("student_answer_id"),
                "prompt_template": prompt_template,
                "model_name": model_name,
                "metrics": metrics,
                "combination_id": combination_id  # Add link to the combination
            }
            
            db_eval = Evaluation(**eval_data)
            db.add(db_eval)
        
        db.commit()
    
    # Transform the evaluation results to match the EvaluationResult schema
    transformed_results = []
    for result in evaluation_result["results"]:
        # Skip results with errors
        if "error" in result and result["error"]:
            transformed_results.append(result)
            continue
        
        # Create EvaluationResult object with all the necessary fields
        transformed_result = {
            "question_id": result.get("question_id"),
            "prompt": result.get("prompt"),
            "response": result.get("response"),
            "extracted_grade": result.get("extracted_grade"),
            "confidence": result.get("confidence"),
            "response_time": result.get("response_time"),
            "error": result.get("error", False),
            "error_message": result.get("error_message"),
            "reference_grade": result.get("reference_grade"),
            "accuracy": result.get("accuracy"),
            "student_answer": None  # Add student answer if available
        }
        transformed_results.append(transformed_result)
    
    # Prepare response
    return {
        "combination_id": combination_id,
        "model_name": model_name,
        "prompt_template": prompt_template,
        "evaluations": transformed_results,
        "metrics": evaluation_result["metrics"]
    }

@router.get("/evaluations", response_model=List[EvaluationSchema])
async def get_evaluations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all evaluations."""
    evaluations = db.query(Evaluation).offset(skip).limit(limit).all()
    return evaluations

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationSchema)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific evaluation by ID."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    return evaluation

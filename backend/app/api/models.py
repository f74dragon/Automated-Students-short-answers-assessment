from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any

from app.database.connection import get_db
from app.models.model import Model
from app.schemas.model_schema import ModelCreate, ModelUpdate, Model as ModelSchema, ModelInfo, ModelList
from app.services.ollama_service import OllamaService
from app.auth.auth import get_current_active_user, get_admin_user

router = APIRouter()
ollama_service = OllamaService()

@router.get("/", response_model=List[ModelSchema])
async def get_models(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all models from the database."""
    models = db.query(Model).offset(skip).limit(limit).all()
    return models

@router.get("/active", response_model=ModelSchema)
async def get_active_model(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get the currently active model."""
    model = db.query(Model).filter(Model.is_active == True).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active model found"
        )
    return model

@router.get("/available", response_model=ModelList)
async def list_available_models(
    current_user = Depends(get_current_active_user)
):
    """List all models available from Ollama."""
    try:
        models = await ollama_service.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )

@router.get("/{model_id}", response_model=ModelSchema)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific model by ID."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model

@router.post("/", response_model=ModelSchema, status_code=status.HTTP_201_CREATED)
async def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can create
):
    """Create a new model entry in the database."""
    # Check if model with the same name already exists
    existing = db.query(Model).filter(Model.name == model.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model with name '{model.name}' already exists"
        )
    
    try:
        db_model = Model(**model.dict())
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating model"
        )

@router.post("/pull", status_code=status.HTTP_202_ACCEPTED)
async def pull_model(
    model_name: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_admin_user)  # Only admins can pull models
):
    """Pull a model from Ollama in the background."""
    # Start downloading the model in the background
    background_tasks.add_task(ollama_service.download_model, model_name)
    
    return {
        "message": f"Model '{model_name}' download started in the background",
        "status": "pending"
    }

@router.put("/{model_id}", response_model=ModelSchema)
async def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can update
):
    """Update an existing model."""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Update fields that are present in the request
    for field, value in model_update.dict(exclude_unset=True).items():
        setattr(db_model, field, value)
    
    try:
        db.commit()
        db.refresh(db_model)
        return db_model
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating model"
        )

@router.put("/{model_id}/activate", response_model=ModelSchema)
async def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can activate
):
    """Set a model as the active one."""
    # First, deactivate all models
    db.query(Model).update({Model.is_active: False})
    
    # Then activate the specified model
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Set the model in the ollama service
    ollama_service.set_model(db_model.name)
    
    # Update the database record
    db_model.is_active = True
    db.commit()
    db.refresh(db_model)
    return db_model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can delete
):
    """Delete a model."""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Don't allow deleting the active model
    if db_model.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active model. Please activate another model first."
        )
    
    db.delete(db_model)
    db.commit()
    return None

@router.post("/{model_id}/update-parameters", response_model=ModelSchema)
async def update_model_parameters(
    model_id: int,
    parameters: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can update parameters
):
    """Update model parameters."""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Update the model parameters
    if db_model.parameters:
        db_model.parameters.update(parameters)
    else:
        db_model.parameters = parameters
    
    # If this is the active model, update the service parameters too
    if db_model.is_active:
        ollama_service.set_parameters(parameters)
    
    db.commit()
    db.refresh(db_model)
    return db_model

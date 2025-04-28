from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.connection import get_db
from app.models.combination import Combination
from app.schemas.evaluation_schema import (
    CombinationCreate, 
    CombinationUpdate, 
    Combination as CombinationSchema, 
    CombinationWithCollections,
    ModelList
)
from app.auth.auth import get_current_active_user
from app.services.ollama_service import OllamaService

router = APIRouter(prefix="/combinations", tags=["combinations"])
ollama_service = OllamaService()

@router.get("/", response_model=List[CombinationSchema])
async def get_combinations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all combinations from the database."""
    combinations = db.query(Combination).offset(skip).limit(limit).all()
    return combinations

@router.get("/models", response_model=ModelList)
async def get_available_models(
    current_user = Depends(get_current_active_user)
):
    """Get all available models from Ollama."""
    try:
        response = await ollama_service._make_request_with_retry("GET", "api/tags")
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch models from Ollama"
            )
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching models: {str(e)}"
        )

@router.get("/{combination_id}", response_model=CombinationWithCollections)
async def get_combination(
    combination_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific combination by ID, including its related collections."""
    combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    return combination

@router.post("/", response_model=CombinationSchema, status_code=status.HTTP_201_CREATED)
async def create_combination(
    combination: CombinationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new combination."""
    # Verify model exists in Ollama
    try:
        response = await ollama_service._make_request_with_retry("GET", "api/tags")
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch models from Ollama"
            )
        
        models = response.json().get("models", [])
        model_exists = any(model["name"] == combination.model_name for model in models)
        
        if not model_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{combination.model_name}' not found in Ollama"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking model: {str(e)}"
        )
    
    # Create the combination
    db_combination = Combination(**combination.model_dump())
    db.add(db_combination)
    db.commit()
    db.refresh(db_combination)
    return db_combination

@router.put("/{combination_id}", response_model=CombinationSchema)
async def update_combination(
    combination_id: int,
    combination_update: CombinationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update an existing combination."""
    db_combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not db_combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    # If model name is being updated, verify it exists in Ollama
    if combination_update.model_name and combination_update.model_name != db_combination.model_name:
        try:
            response = await ollama_service._make_request_with_retry("GET", "api/tags")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch models from Ollama"
                )
            
            models = response.json().get("models", [])
            model_exists = any(model["name"] == combination_update.model_name for model in models)
            
            if not model_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model '{combination_update.model_name}' not found in Ollama"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking model: {str(e)}"
            )
    
    # Update fields that are present in the request
    for field, value in combination_update.model_dump(exclude_unset=True).items():
        setattr(db_combination, field, value)
    
    db.commit()
    db.refresh(db_combination)
    return db_combination

@router.delete("/{combination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_combination(
    combination_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a combination."""
    db_combination = db.query(Combination).filter(Combination.id == combination_id).first()
    if not db_combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    # Check if this combination is used by any collections
    if db_combination.collections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete combination that is in use by collections"
        )
    
    db.delete(db_combination)
    db.commit()
    return None

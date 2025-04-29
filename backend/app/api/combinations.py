from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging

from app.database.connection import get_db
from app.models.combination import Combination
from app.schemas.evaluation_schema import (
    CombinationCreate, 
    CombinationUpdate, 
    Combination as CombinationSchema, 
    CombinationWithCollections,
    ModelList
)
from app.auth.auth import get_current_active_user, get_admin_user
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

@router.post("/pull")
async def pull_model(
    model_request: dict,
    current_user = Depends(get_admin_user)  # Ensure only admins can pull models
):
    """Pull a new model from Ollama with streaming progress updates."""
    model_name = model_request.get("model_name")
    if not model_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model name is required"
        )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting model pull for '{model_name}'")
    
    # Create async generator to stream progress updates
    async def progress_stream():
        service = OllamaService()
        
        # First check if model exists
        exists = await service.check_model_exists(model_name)
        if exists:
            logger.info(f"Model '{model_name}' already exists")
            yield json.dumps({"status": "success", "message": f"Model '{model_name}' already exists"}) + "\n"
            return
            
        # If model doesn't exist, stream download progress
        try:
            async for progress in service.stream_download_progress(model_name):
                # Convert progress data to JSON string and yield
                if "error" in progress:
                    logger.error(f"Error in download: {progress['error']}")
                    yield json.dumps({"status": "error", "message": progress["error"]}) + "\n"
                    return
                
                # Enhance logging for download progress
                if progress.get("status") == "downloading":
                    completed = progress.get("completed", 0)
                    total = progress.get("total", 0)
                    percentage = (completed / total) * 100 if total > 0 else 0
                    digest = progress.get("digest", "unknown")
                    
                    completed_mb = round(completed / (1024 * 1024), 2)
                    total_mb = round(total / (1024 * 1024), 2)
                    
                    logger.info(f"Downloading {digest}: {completed_mb} MB / {total_mb} MB ({percentage:.1f}%)")
                else:
                    logger.info(f"Status update: {progress.get('status')}")
                
                # Send the complete progress data to the frontend
                yield json.dumps(progress) + "\n"
            
            # Final success message
            yield json.dumps({"status": "success", "message": f"Model '{model_name}' pulled successfully"}) + "\n"
            
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            yield json.dumps({"status": "error", "message": f"Error pulling model: {str(e)}"}) + "\n"
    
    # Return a streaming response with the progress updates
    return StreamingResponse(
        progress_stream(),
        media_type="text/event-stream"
    )

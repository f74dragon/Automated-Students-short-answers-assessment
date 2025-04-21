from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database.connection import get_db
from app.models.prompt import Prompt
from app.schemas.prompt_schema import PromptCreate, PromptUpdate, Prompt as PromptSchema, PromptWithMetrics
from app.auth.auth import get_current_active_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[PromptSchema])
async def get_prompts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all prompts."""
    prompts = db.query(Prompt).offset(skip).limit(limit).all()
    return prompts

@router.get("/active", response_model=PromptSchema)
async def get_active_prompt(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get the currently active prompt."""
    prompt = db.query(Prompt).filter(Prompt.is_active == True).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active prompt found"
        )
    return prompt

@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific prompt by ID."""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return prompt

@router.post("/", response_model=PromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt: PromptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can create
):
    """Create a new prompt."""
    try:
        db_prompt = Prompt(**prompt.dict())
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating prompt"
        )

@router.put("/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can update
):
    """Update an existing prompt."""
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Update fields that are present in the request
    for field, value in prompt_update.dict(exclude_unset=True).items():
        setattr(db_prompt, field, value)
    
    try:
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating prompt"
        )

@router.put("/{prompt_id}/activate", response_model=PromptSchema)
async def activate_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can activate
):
    """Set a prompt as the active one."""
    # First, deactivate all prompts
    db.query(Prompt).update({Prompt.is_active: False})
    
    # Then activate the specified prompt
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    db_prompt.is_active = True
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can delete
):
    """Delete a prompt."""
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Don't allow deleting the active prompt
    if db_prompt.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active prompt. Please activate another prompt first."
        )
    
    db.delete(db_prompt)
    db.commit()
    return None

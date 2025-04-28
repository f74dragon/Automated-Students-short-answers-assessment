from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.models.prompt import Prompt
from app.schemas.prompt_schema import PromptCreate, PromptUpdate, Prompt as PromptSchema, CategoryList
from app.auth.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/prompts", tags=["prompts"])

@router.get("/", response_model=List[PromptSchema])
async def get_prompts(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all prompts, with optional category filter."""
    query = db.query(Prompt)
    if category:
        query = query.filter(Prompt.category == category)
    prompts = query.offset(skip).limit(limit).all()
    return prompts

@router.post("/", response_model=PromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt: PromptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create a new prompt."""
    db_prompt = Prompt(**prompt.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get a specific prompt by ID."""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return prompt

@router.put("/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Update an existing prompt."""
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    for field, value in prompt_update.model_dump(exclude_unset=True).items():
        setattr(db_prompt, field, value)
    
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Delete a prompt."""
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    db.delete(db_prompt)
    db.commit()
    return None

@router.get("/categories/all", response_model=CategoryList)
async def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all unique categories."""
    categories = [row[0] for row in db.query(Prompt.category).distinct().all()]
    return {"categories": categories}

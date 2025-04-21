from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from app.services.ollama_service import OllamaService
from app.auth.auth import get_current_user

# Initialize the Ollama service
ollama_service = OllamaService(
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    max_retries=3,
    initial_retry_delay=1.0
)

# Define API router
router = APIRouter()

# Define request models
class PromptUpdate(BaseModel):
    template: str
    
# Define response models
class PromptResponse(BaseModel):
    template: str
    is_default: bool

@router.get("/", response_model=PromptResponse)
async def get_prompt(current_user = Depends(get_current_user)):
    """Get the current prompt template."""
    try:
        current_template = ollama_service.get_prompt_template()
        is_default = current_template == ollama_service.default_prompt_template
        
        return PromptResponse(
            template=current_template,
            is_default=is_default
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update", response_model=PromptResponse)
async def update_prompt(prompt_update: PromptUpdate, current_user = Depends(get_current_user)):
    """Update the prompt template."""
    try:
        success = ollama_service.update_prompt_template(prompt_update.template)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid prompt template")
        
        current_template = ollama_service.get_prompt_template()
        is_default = current_template == ollama_service.default_prompt_template
        
        return PromptResponse(
            template=current_template,
            is_default=is_default
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset", response_model=PromptResponse)
async def reset_prompt(current_user = Depends(get_current_user)):
    """Reset the prompt template to default."""
    try:
        success = ollama_service.reset_prompt_template()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset prompt template")
        
        return PromptResponse(
            template=ollama_service.default_prompt_template,
            is_default=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

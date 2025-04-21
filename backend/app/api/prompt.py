from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from app.services.ollama_service import OllamaService

# We'll dynamically get the singleton instance in each endpoint

# Define API router
router = APIRouter()

# Add a public endpoint for testing
@router.get("/status", response_model=dict)
async def get_status():
    """Check if the prompt service is available (no auth required)."""
    try:
        # Get the singleton instance
        ollama_service = await OllamaService.get_instance()
        return {
            "status": "available",
            "default_template_available": bool(ollama_service.default_prompt_template),
            "service_initialized": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define request models
class PromptUpdate(BaseModel):
    template: str
    
# Define response models
class PromptResponse(BaseModel):
    template: str
    is_default: bool

@router.get("/", response_model=PromptResponse)
async def get_prompt():
    """Get the current prompt template."""
    try:
        # Get the singleton instance
        ollama_service = await OllamaService.get_instance()
        current_template = ollama_service.get_prompt_template()
        is_default = current_template == ollama_service.default_prompt_template
        
        return PromptResponse(
            template=current_template,
            is_default=is_default
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update", response_model=PromptResponse)
async def update_prompt(prompt_update: PromptUpdate):
    """Update the prompt template."""
    try:
        # Get the singleton instance
        ollama_service = await OllamaService.get_instance()
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
async def reset_prompt():
    """Reset the prompt template to default."""
    try:
        # Get the singleton instance
        ollama_service = await OllamaService.get_instance()
        success = ollama_service.reset_prompt_template()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset prompt template")
        
        return PromptResponse(
            template=ollama_service.default_prompt_template,
            is_default=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
import os
from llm.services.ollama_service import OllamaService

router = APIRouter()
ollama_service = OllamaService(
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    max_retries=3,
    initial_retry_delay=1.0
)

@router.get("/status")
async def get_model_status():
    """Check if the model is downloaded and available."""
    try:
        exists = await ollama_service.check_model_exists()
        return {
            "status": "available" if exists else "not_found",
            "model": ollama_service.model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_model_info():
    """Get detailed information about the model."""
    try:
        info = await ollama_service.get_model_info()
        if not info:
            raise HTTPException(status_code=404, detail="Model information not available")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

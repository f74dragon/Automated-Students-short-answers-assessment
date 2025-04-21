import sys, requests
from pathlib import Path
# app/main.py
from fastapi import FastAPI, HTTPException
from app.services.ollama_service import OllamaService
from fastapi.middleware.cors import CORSMiddleware
from app.api.users import router as users_router
from app.api.login import router as login_router
from app.api.collections import router as collections_router
from app.api.students import router as students_router
from app.api.questions import router as questions_router
from app.api.student_answers import router as student_answers_router
from app.api.prompt import router as prompt_router
from app.api.models import router as models_router
from app.api.evaluation import router as evaluation_router
from app.api.model import router as model_router
from app.database.connection import init_db

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    """Initialize the LLM model on startup."""
    # Initialize Ollama service
    ollama_service = OllamaService()
    try:
        # Check if model exists and download if needed
        model_exists = await ollama_service.check_model_exists()
        if not model_exists:
            await ollama_service.download_model()
    except Exception as e:
        print(f"Failed to initialize Ollama service: {e}")

# Include the model-related routers
app.include_router(model_router, prefix="/api/model", tags=["model"])
app.include_router(prompt_router, prefix="/api/prompts", tags=["prompts"])
app.include_router(models_router, prefix="/api/models", tags=["models"])
app.include_router(evaluation_router, prefix="/api/evaluations", tags=["evaluations"])

# Import CSV evaluation router
from app.api.csv_evaluation import router as csv_evaluation_router
app.include_router(csv_evaluation_router, prefix="/api/csv-evaluation", tags=["csv"])

@app.post("/api/generate")
async def generate_text(prompt: str):
    """Generate text using the LLM model."""
    ollama_service = OllamaService()
    response = await ollama_service.generate_response(prompt)
    return {"response": response.get("text", "")}

app.include_router(users_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(collections_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(student_answers_router, prefix="/api")

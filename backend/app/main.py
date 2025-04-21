import sys, requests
from pathlib import Path
# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.users import router as users_router
from app.api.login import router as login_router
from app.api.collections import router as collections_router
from app.api.students import router as students_router
from app.api.questions import router as questions_router
from app.api.student_answers import router as student_answers_router
from app.api.prompt import router as prompt_router
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
    # initializer = get_model_initializer()
    # success = await initializer.initialize()
    # if not success:
    #     raise Exception("Failed to initialize LLM model")

# Include the model router
# app.include_router(model_router.router, prefix="/api/model", tags=["model"])

@app.post("/api/generate")
async def generate_text(prompt: str):
    """Generate text using the LLM model."""
    # The GPU detection and configuration happens in the standalone Ollama installation
    # so we don't need to specify any GPU options here
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:14b",
            "prompt": prompt,
            "stream": False
            # Hardware detection is handled by the standalone Ollama installation
        }
    )
    return response.json()

app.include_router(users_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(collections_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(student_answers_router, prefix="/api")
app.include_router(prompt_router, prefix="/api/prompt", tags=["prompt"])

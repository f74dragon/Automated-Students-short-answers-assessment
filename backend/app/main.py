from fastapi import FastAPI, HTTPException
import sys, requests
from pathlib import Path

from llm.services.model_initializer import get_model_initializer
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from app.api import model as model_router
=======
from app.api.users import router as users_router
from app.api.login import router as login_router
from app.api.collections import router as collections_router
from app.api.students import router as students_router
from app.api.questions import router as questions_router
from app.api.student_answers import router as student_answers_router
from app.database.connection import init_db
>>>>>>> cd6c6e1 (Added LLM control and frontend changes)

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
    """Initialize the LLM model on startup."""
    initializer = get_model_initializer()
    success = await initializer.initialize()
    if not success:
        raise Exception("Failed to initialize LLM model")

# Include the model router
app.include_router(model_router.router, prefix="/api/model", tags=["model"])

@app.post("/api/generate")
async def generate_text(prompt: str):
    """Generate text using the LLM model."""
    response = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": "deepseek-r1:14b",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()
<<<<<<< HEAD
=======

app.include_router(users_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(collections_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(student_answers_router, prefix="/api")
>>>>>>> cd6c6e1 (Added LLM control and frontend changes)

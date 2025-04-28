import sys
from pathlib import Path
# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from app.services.ollama_service import OllamaService
from app.api.users import router as users_router
from app.api.login import router as login_router
from app.api.collections import router as collections_router
from app.api.combinations import router as combinations_router
from app.api.students import router as students_router
from app.api.questions import router as questions_router
from app.api.student_answers import router as student_answers_router
from app.database.connection import init_db

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    """Initialize the database and create default combination if needed."""
    
    # Create default combination if none exists
    from sqlalchemy.orm import Session
    from app.database.connection import get_db
    from app.models.combination import Combination
    
    db = next(get_db())
    combination_count = db.query(Combination).count()
    
    # Default prompt template for grading
    DEFAULT_PROMPT = """Question: {{question}}

Correct Answer: {{model_answer}}

Student's Answer: {{student_answer}}

Grade the student's answer based on the correct answer from (0.0 - 1.0). 
Provide a brief explanation for your grade."""
    
    if combination_count == 0:
        # Create default combination
        default_combination = Combination(
            name="Default Grading Pair",
            description="Default grading prompt and model for student answer evaluation",
            prompt=DEFAULT_PROMPT,
            model_name="gemma3:4b"
        )
        
        db.add(default_combination)
        db.commit()
        print("Created default combination with gemma3:4b model")

# Include the model router
# app.include_router(model_router.router, prefix="/api/model", tags=["model"])

# Initialize OllamaService
ollama_service = OllamaService()

@app.post("/api/generate")
async def generate_text(prompt: str):
    """Generate text using the LLM model."""
    try:
        response = await ollama_service._make_request_with_retry(
            "POST",
            "api/generate",
            json={
                "model": "deepseek-r1:14b",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

app.include_router(users_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(collections_router, prefix="/api")
app.include_router(combinations_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(student_answers_router, prefix="/api")

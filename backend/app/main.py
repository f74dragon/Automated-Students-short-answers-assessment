from fastapi import FastAPI, HTTPException
import sys, requests
from pathlib import Path

from llm.services.model_initializer import get_model_initializer
from fastapi.middleware.cors import CORSMiddleware
from app.api import model as model_router

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

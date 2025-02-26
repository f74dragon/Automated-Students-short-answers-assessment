from fastapi import FastAPI
import requests

app = FastAPI()

@app.post("/api/generate")
async def generate_text(prompt: str):
    response = requests.post(
        "http://ollama:11434/v1/completions",
        json={"model": "llama2", "prompt": prompt}
    )
    return response.json()

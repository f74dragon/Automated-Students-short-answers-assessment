import httpx
import logging
import os
import asyncio
import re
from typing import Dict, Optional, Tuple

class OllamaService:
    def __init__(self, base_url: str = None, max_retries: int = 5, initial_retry_delay: float = 1.0):
        self.base_url = base_url or os.environ.get("OLLAMA_URL", "http://ollama:11434")
        self.model_name = "gemma3:4b"
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay

    async def _make_request_with_retry(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request with exponential backoff retry logic."""
        delay = self.initial_retry_delay
        last_exception = None

        for retry in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method,
                        f"{self.base_url}/{endpoint}",
                        **kwargs,
                        timeout=30.0
                    )
                    return response
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Request failed (attempt {retry + 1}/{self.max_retries}): {str(e)}")
                if retry < self.max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff

        raise last_exception or Exception("All retry attempts failed")

    async def check_model_exists(self) -> bool:
        """Check if the model is already downloaded."""
        self.logger.info("Checking if model exists...")
        try:
            response = await self._make_request_with_retry("GET", "api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                exists = any(model["name"] == self.model_name for model in models)
                self.logger.info(f"Model {'exists' if exists else 'does not exist'}")
                return exists
            return False
        except Exception as e:
            self.logger.error(f"Error checking model existence: {e}")
            return False

    async def download_model(self) -> bool:
        """Download the model if it doesn't exist."""
        try:
            if await self.check_model_exists():
                self.logger.info(f"Model {self.model_name} already exists")
                return True

            self.logger.info(f"Downloading model {self.model_name}...")
            response = await self._make_request_with_retry(
                "POST",
                "api/pull",
                json={"name": self.model_name}
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully downloaded model {self.model_name}")
                return True
            else:
                self.logger.error(f"Failed to download model: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            return False

    async def get_model_info(self) -> Optional[Dict]:
        """Get information about the downloaded model."""
        try:
            response = await self._make_request_with_retry(
                "POST",
                "api/show",
                json={"name": self.model_name}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return None
            
    async def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM using the given prompt."""
        try:
            self.logger.info(f"Generating response for prompt: {prompt[:50]}...")
            response = await self._make_request_with_retry(
                "POST",
                "api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                self.logger.error(f"Failed to generate response: {response.text}")
                return ""
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return ""
    
    def extract_grade(self, response: str) -> Tuple[float, str]:
        """
        Extract a grade from the model's response.
        
        Args:
            response: Text response from the model
            
        Returns:
            Tuple of (extracted_grade, confidence_level)
        """
        # Try to find a grade in format "Grade: X.X" or similar
        grade_pattern = r"(?:grade|score|rating|mark):\s*([0-9]\.[0-9]|[01])"
        match = re.search(grade_pattern, response.lower())
        
        if match:
            return float(match.group(1)), "high"
        
        # Try to find a standalone decimal between 0 and 1
        decimal_pattern = r"(?<![a-zA-Z0-9])([0-9]\.[0-9]|[01])(?![0-9])"
        matches = re.findall(decimal_pattern, response)
        
        if matches:
            # If multiple matches, take the last one as it's likely the conclusion
            return float(matches[-1]), "medium"
        
        # Look for numbers written as words
        word_to_grade = {
            "zero": 0.0, "one": 1.0, "half": 0.5,
            "zero point five": 0.5, "point five": 0.5,
            "0": 0.0, "1": 1.0, "0.5": 0.5
        }
        
        for word, grade in word_to_grade.items():
            if word in response.lower():
                return grade, "low"
        
        # Default fallback
        return 0.5, "very low"
    
    def extract_feedback(self, response: str) -> str:
        """
        Extract feedback from the model's response.
        
        Args:
            response: Text response from the model
            
        Returns:
            Extracted feedback or empty string if none found
        """
        # Remove the grade part if present
        grade_pattern = r"(?:grade|score|rating|mark):\s*([0-9]\.[0-9]|[01])"
        feedback = re.sub(grade_pattern, "", response, flags=re.IGNORECASE)
        
        # Clean up the feedback
        feedback = feedback.strip()
        
        return feedback
    
    def create_grading_prompt(self, question: str, model_answer: str, student_answer: str) -> str:
        """
        Create a prompt for the model to grade a student's answer.
        
        Args:
            question: The question being asked
            model_answer: The correct answer
            student_answer: The student's answer to grade
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Question: {question}

Correct Answer: {model_answer}

Student's Answer: {student_answer}

Grade the student's answer based on the correct answer from (0.0 - 1.0). 
Provide a brief explanation for your grade.
"""
        return prompt

import httpx
import logging
import os
import asyncio
import re
import json
from typing import Dict, Optional, Tuple, List, Any

class OllamaService:
    def __init__(self, base_url: str = None, max_retries: int = 5, initial_retry_delay: float = 1.0):
        self.base_url = base_url or os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model_name = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.default_parameters = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
        }

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
    
    def set_model(self, model_name: str) -> None:
        """Set the current model to use for generation."""
        self.model_name = model_name
        self.logger.info(f"Model set to {model_name}")
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update the default parameters for generation."""
        self.default_parameters.update(parameters)
        self.logger.info(f"Parameters updated: {parameters}")

    async def check_model_exists(self, model_name: Optional[str] = None) -> bool:
        """Check if the model is already downloaded."""
        model_name = model_name or self.model_name
        self.logger.info(f"Checking if model {model_name} exists...")
        try:
            response = await self._make_request_with_retry("GET", "api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                exists = any(model["name"] == model_name for model in models)
                self.logger.info(f"Model {model_name} {'exists' if exists else 'does not exist'}")
                return exists
            return False
        except Exception as e:
            self.logger.error(f"Error checking model existence: {e}")
            return False

    async def download_model(self, model_name: Optional[str] = None) -> bool:
        """Download the model if it doesn't exist."""
        model_name = model_name or self.model_name
        try:
            if await self.check_model_exists(model_name):
                self.logger.info(f"Model {model_name} already exists")
                return True

            self.logger.info(f"Downloading model {model_name}...")
            response = await self._make_request_with_retry(
                "POST",
                "api/pull",
                json={"name": model_name}
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully downloaded model {model_name}")
                return True
            else:
                self.logger.error(f"Failed to download model: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            return False

    async def get_model_info(self, model_name: Optional[str] = None) -> Optional[Dict]:
        """Get information about the downloaded model."""
        model_name = model_name or self.model_name
        try:
            response = await self._make_request_with_retry(
                "POST",
                "api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return None
            
    async def generate_response(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a response from the LLM using the given prompt."""
        try:
            self.logger.info(f"Generating response for prompt: {prompt[:50]}...")
            
            # Combine default parameters with any provided parameters
            request_params = self.default_parameters.copy()
            if parameters:
                request_params.update(parameters)
                
            # Create full request body
            request_body = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                **request_params
            }
            
            start_time = asyncio.get_event_loop().time()
            response = await self._make_request_with_retry(
                "POST",
                "api/generate",
                json=request_body
            )
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "text": result.get("response", ""),
                    "raw_response": result,
                    "response_time": response_time,
                    "error": False
                }
            else:
                error_msg = f"Failed to generate response: {response.text}"
                self.logger.error(error_msg)
                return {
                    "text": "",
                    "error": True,
                    "error_message": error_msg,
                    "response_time": response_time
                }
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            return {
                "text": "",
                "error": True,
                "error_message": error_msg,
                "response_time": 0.0
            }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models."""
        try:
            response = await self._make_request_with_retry("GET", "api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
            else:
                self.logger.error(f"Failed to list models: {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
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
    
    def create_grading_prompt(self, question: str, model_answer: str, student_answer: str, prompt_template: Optional[str] = None) -> str:
        """
        Create a prompt for the model to grade a student's answer.
        
        Args:
            question: The question being asked
            model_answer: The correct answer
            student_answer: The student's answer to grade
            prompt_template: Optional custom prompt template with placeholders
            
        Returns:
            Formatted prompt string
        """
        if prompt_template:
            # Replace placeholders in custom template
            return (prompt_template
                    .replace("{question}", question)
                    .replace("{model_answer}", model_answer)
                    .replace("{student_answer}", student_answer))
        
        # Default template
        prompt = f"""Question: {question}

Correct Answer: {model_answer}

Student's Answer: {student_answer}

Grade the student's answer based on the correct answer from (0.0 - 1.0). 
Provide a brief explanation for your grade.
"""
        return prompt
    
    async def evaluate_model_prompt(self, model_name: str, prompt_template: str, 
                                   questions: List[Dict], parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate a model and prompt combination on a set of questions.
        
        Args:
            model_name: Name of the model to use
            prompt_template: Prompt template to use
            questions: List of questions with model answers and student answers
            parameters: Optional model parameters
            
        Returns:
            Dictionary with evaluation results and metrics
        """
        # Save current model and create temp instance
        current_model = self.model_name
        self.model_name = model_name
        
        results = []
        total_accuracy = 0.0
        total_response_time = 0.0
        errors = 0
        
        for question in questions:
            try:
                # Create prompt using the template
                prompt = self.create_grading_prompt(
                    question["text"], 
                    question["model_answer"], 
                    question["student_answer"],
                    prompt_template
                )
                
                # Get model response
                response_data = await self.generate_response(prompt, parameters)
                
                if response_data["error"]:
                    errors += 1
                    results.append({
                        "question_id": question.get("id"),
                        "error": True,
                        "error_message": response_data["error_message"],
                        "response_time": 0.0
                    })
                    continue
                
                # Extract grade and calculate accuracy if we have a reference grade
                extracted_grade, confidence = self.extract_grade(response_data["text"])
                accuracy = 0.0
                
                if "reference_grade" in question:
                    accuracy = 1.0 - abs(extracted_grade - float(question["reference_grade"]))
                    total_accuracy += accuracy
                
                # Store result
                result = {
                    "question_id": question.get("id"),
                    "prompt": prompt,
                    "response": response_data["text"],
                    "extracted_grade": extracted_grade,
                    "confidence": confidence,
                    "response_time": response_data["response_time"],
                    "error": False
                }
                
                if "reference_grade" in question:
                    result["reference_grade"] = float(question["reference_grade"])
                    result["accuracy"] = accuracy
                
                results.append(result)
                total_response_time += response_data["response_time"]
                
            except Exception as e:
                self.logger.error(f"Error evaluating question: {e}")
                errors += 1
                results.append({
                    "question_id": question.get("id"),
                    "error": True,
                    "error_message": str(e),
                    "response_time": 0.0
                })
        
        # Calculate aggregate metrics
        successful_evals = len(questions) - errors
        metrics = {
            "total_questions": len(questions),
            "successful_evaluations": successful_evals,
            "errors": errors,
            "average_response_time": total_response_time / max(successful_evals, 1),
        }
        
        # Add accuracy if we have reference grades
        questions_with_grades = sum(1 for q in questions if "reference_grade" in q)
        if questions_with_grades > 0:
            metrics["average_accuracy"] = total_accuracy / questions_with_grades
        
        # Restore original model
        self.model_name = current_model
        
        return {
            "model": model_name,
            "prompt_template": prompt_template,
            "parameters": parameters,
            "results": results,
            "metrics": metrics
        }

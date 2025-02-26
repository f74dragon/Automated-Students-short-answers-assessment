import httpx
import logging
import os
import asyncio
from typing import Dict, Optional

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434", max_retries: int = 5, initial_retry_delay: float = 1.0):
        self.base_url = base_url
        self.model_name = "deepseek-r1:14b"
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

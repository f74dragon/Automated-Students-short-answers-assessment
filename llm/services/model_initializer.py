import asyncio
import os
from typing import Optional
from .ollama_service import OllamaService
from ..utils.logging_config import setup_logging

class ModelInitializer:
    def __init__(self):
        self.logger = setup_logging()
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_service = OllamaService(
            base_url=ollama_url,
            max_retries=5,
            initial_retry_delay=2.0
        )

    async def initialize(self) -> bool:
        """Initialize the model on startup."""
        self.logger.info("Starting model initialization...")
        
        try:
            # Attempt to download the model
            download_success = await self.ollama_service.download_model()
            if not download_success:
                self.logger.error("Failed to download/verify model")
                return False

            # Get model info to verify everything is working
            model_info = await self.ollama_service.get_model_info()
            if not model_info:
                self.logger.error("Could not retrieve model info after download")
                return False

            self.logger.info("Model initialization completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            return False

def get_model_initializer() -> ModelInitializer:
    """Factory function for model initializer."""
    return ModelInitializer()

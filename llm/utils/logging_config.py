import logging
import sys
from pathlib import Path

def setup_logging():
    """Configure logging for the LLM service."""
    # Create logs directory if it doesn't exist
    log_dir = Path("llm/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "llm_service.log")
        ]
    )

    # Create logger
    logger = logging.getLogger("llm_service")
    return logger

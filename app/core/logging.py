import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings

# Remove default logger
logger.remove()

# Add console logger with appropriate level
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add file logger
log_file = Path("logs/cv_parser.log")
log_file.parent.mkdir(parents=True, exist_ok=True)

logger.add(
    log_file,
    rotation="10 MB",
    retention="1 month",
    compression="zip",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

def get_logger():
    """Get the configured logger instance."""
    return logger 
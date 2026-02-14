"""
Logging Configuration
Sets up consistent logging for backend and frontend
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Configure logging for a component
    
    Args:
        name: Logger name (e.g., 'backend', 'frontend')
        log_file: Optional path to log file
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            str(log_path),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default loggers
backend_logger = setup_logging(
    "backend",
    str(Path.home() / ".content-studio" / "app.log"),
    level=logging.INFO
)

frontend_logger = setup_logging(
    "frontend",
    str(Path.home() / ".content-studio" / "streamlit.log"),
    level=logging.INFO
)

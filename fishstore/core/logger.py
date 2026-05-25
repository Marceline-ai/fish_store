"""
Logger module with rotation support.
Implements logging requirements from section 3.2 of the specification.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger():
    """
    Setup application logger with file rotation.
    
    Configuration:
    - Max file size: 5 MB (as per spec)
    - Backup count: 3 archives (as per spec)
    - Format: timestamp, level, module, message
    """
    # Get log settings from environment or use defaults
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    max_size_mb = int(os.getenv('LOG_MAX_SIZE_MB', '5'))
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', '3'))
    
    # Create logs directory if not exists
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file path with date
    log_file = os.path.join(log_dir, f'fishstore_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Create logger
    logger = logging.getLogger('FishStore')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size_mb * 1024 * 1024,  # Convert MB to bytes
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
_logger = None


def get_logger():
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger

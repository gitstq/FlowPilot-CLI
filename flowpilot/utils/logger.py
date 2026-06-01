"""
Logging utilities
"""

import logging
import os
from typing import Optional


def setup_logging(level: Optional[str] = None):
    """Setup logging configuration"""
    if level is None:
        level = os.environ.get('FLOWPILOT_LOG_LEVEL', 'INFO')
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Suppress noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    logger = logging.getLogger(name)
    
    # Ensure logging is setup
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logger

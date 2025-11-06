import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "connect_four", log_level: Optional[int] = None
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: The name of the logger
        log_level: Optional logging level (defaults to INFO if not specified)

    Returns:
        logging.Logger: Configured logger instance
    """
    if log_level is None:
        log_level = logging.INFO

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create console handler and set level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logger()

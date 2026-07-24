"""Structured logging utility for ARC-AGI-3 Research Agent."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "arc_agent",
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Configure and return a structured logger instance.

    Args:
        name: Name of the logger instance.
        log_level: Logging level (e.g. logging.DEBUG, logging.INFO).
        log_file: Optional Path to write log output to a file.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid adding duplicate handlers if already configured
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional File Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "arc_agent") -> logging.Logger:
    """Retrieve an existing logger or set up a default one."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

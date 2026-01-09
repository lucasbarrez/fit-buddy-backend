import sys
from pathlib import Path
from typing import Any

from loguru import logger


def setup_logging() -> Any:
    """Setup the logger"""

    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=True,
    )

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger.add(
        logs_dir / "app.log",
        format=log_format,
        level="DEBUG",
        rotation="10 MB",
        retention="1 days",
        compression="zip",
    )

    return logger


app_logger = setup_logging()

import os

from loguru import logger


def setup_logging():
    """Базовая настройка логгера для всего проекта."""

    log_dir = ".log"
    os.makedirs(log_dir, exist_ok=True)

    logger.add(
        ".log/log.json",
        format="{time} {level} {message}",
        level="DEBUG",
        rotation="1 week",
        compression="zip",
        serialize=True,
    )
    return logger

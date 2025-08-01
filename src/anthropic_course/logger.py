"""Logger configuration for anthropic-course."""

from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log levels enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig(BaseModel):
    """Configuration for logging."""

    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        description="Log format string",
    )
    colorize: bool = Field(default=True, description="Enable colorized output")
    show_time: bool = Field(default=True, description="Show timestamp in logs")


def configure_logger(config: LogConfig | None = None) -> None:
    """Configure loguru logger with custom settings.

    Args:
        config: LogConfig instance with logger settings. If None, uses defaults.
    """
    if config is None:
        config = LogConfig()

    # Remove default handler
    logger.remove()

    # Add custom handler with configuration
    logger.add(
        lambda msg: print(msg, end=""),
        format=config.format,
        level=config.level.value,
        colorize=config.colorize,
    )


def get_logger():
    """Get configured logger instance.

    Returns:
        Configured loguru logger instance.
    """
    return logger


# Configure logger on module import
configure_logger()

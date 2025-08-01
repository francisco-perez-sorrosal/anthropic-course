"""Main CLI application for anthropic-course."""

import os

import typer
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .logger import get_logger
from . import __version__

# Load environment variables
load_dotenv()

# Initialize Typer app and Rich console
app = typer.Typer(
    name="anthropic-course",
    help="A simple Python toy/POC project",
    add_completion=False,
)
console = Console()

# Get configured logger
logger = get_logger()


class AppConfig(BaseModel):
    """Application configuration model."""

    debug: bool = Field(default=False, description="Enable debug mode")
    app_name: str = Field(default="Anthropic Course", description="Application name")
    version: str = Field(default=__version__, description="Application version")

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create AppConfig from environment variables."""
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            app_name=os.getenv("APP_NAME", "Anthropic Course"),
            version=os.getenv("VERSION", __version__),
        )


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
) -> None:
    """Main application entry point with colorful logging demonstration."""

    # Load configuration
    config = AppConfig.from_env()
    if debug:
        config.debug = True

    # Update logger level if debug is enabled
    if config.debug:
        from .logger import LogConfig, LogLevel, configure_logger

        debug_config = LogConfig(level=LogLevel.DEBUG)
        configure_logger(debug_config)
        # Get fresh logger instance after reconfiguration
        from .logger import get_logger

        global logger
        logger = get_logger()

    # Display startup banner
    banner_text = Text(f"🚀 {config.app_name}", style="bold blue")
    banner_text.append("\n✨ Simple Toy/POC Project", style="italic green")
    banner_text.append(f"\n📦 Version: {config.version}", style="yellow")

    console.print(Panel(banner_text, border_style="blue"))

    # Demonstrate all log levels with colors
    logger.debug("🔍 Debug mode enabled - showing detailed information")
    logger.info("ℹ️  Application started successfully")
    logger.warning("⚠️  This is a warning message")
    logger.error("❌ This is an error message")
    logger.critical("🚨 This is a critical error!")

    # Fun info messages with rich formatting
    logger.info(
        "🎨 [bold blue]Rich[/bold blue] formatting works with [italic green]loguru[/italic green]!"
    )
    logger.info(
        "🌈 [red]Colors[/red] [yellow]are[/yellow] [green]beautiful[/green] [blue]and[/blue] [magenta]fun[/magenta]!"
    )
    logger.info(
        "⚡ [bold]Fast[/bold] and [italic]efficient[/italic] logging with [underline]style[/underline]!"
    )

    # Demonstrate Pydantic validation
    try:
        # This should work
        valid_config = AppConfig(debug=True, app_name="Test App", version="1.0.0")
        logger.info(f"✅ Pydantic validation successful: {valid_config.app_name}")

        # This would raise validation error (commented out to avoid actual error)
        # invalid_config = AppConfig(debug="not_a_boolean")  # This would fail

    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")

    # Success message
    success_text = Text("✅ All systems operational!", style="bold green")
    console.print(Panel(success_text, border_style="blue"))


if __name__ == "__main__":
    app()

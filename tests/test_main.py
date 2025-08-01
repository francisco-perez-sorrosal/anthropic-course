"""Tests for main application."""

import pytest
from typer.testing import CliRunner

from anthropic_course.logger import LogConfig, LogLevel
from anthropic_course.main import AppConfig, app


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_app_config_creation():
    """Test AppConfig creation and validation."""
    config = AppConfig(debug=True, app_name="Test App", version="0.0.1")

    assert config.debug is True
    assert config.app_name == "Test App"
    assert config.version == "0.0.1"


def test_app_config_defaults():
    """Test AppConfig default values."""
    config = AppConfig()

    assert config.debug is False
    assert config.app_name == "Anthropic Course"
    assert config.version == "0.0.1"


def test_log_config_creation():
    """Test LogConfig creation and validation."""
    config = LogConfig(level=LogLevel.DEBUG, colorize=False)

    assert config.level == LogLevel.DEBUG
    assert config.colorize is False
    assert config.show_time is True  # default value


def test_log_level_enum():
    """Test LogLevel enum values."""
    assert LogLevel.DEBUG.value == "DEBUG"
    assert LogLevel.INFO.value == "INFO"
    assert LogLevel.WARNING.value == "WARNING"
    assert LogLevel.ERROR.value == "ERROR"
    assert LogLevel.CRITICAL.value == "CRITICAL"


def test_cli_help(cli_runner):
    """Test CLI help command."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "main" in result.output  # The command name is 'main'
    assert "Main application entry point" in result.output


def test_cli_main_command(cli_runner):
    """Test main CLI command execution."""
    result = cli_runner.invoke(app, [])
    assert result.exit_code == 0
    assert "🚀 Anthropic Course" in result.output
    assert "✅ All systems operational!" in result.output


def test_cli_debug_mode(cli_runner):
    """Test CLI debug mode."""
    result = cli_runner.invoke(app, ["--debug"])
    assert result.exit_code == 0
    assert "DEBUG" in result.output  # Debug level should be visible in output


def test_app_config_from_env(monkeypatch):
    """Test AppConfig creation from environment variables."""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("APP_NAME", "Custom App")
    monkeypatch.setenv("VERSION", "2.0.0")

    config = AppConfig.from_env()

    assert config.debug is True
    assert config.app_name == "Custom App"
    assert config.version == "2.0.0"

"""Tests for configuration validator."""
import pytest
from modules.config_validator import validate_config


def test_valid_config():
    """Test that a valid config passes validation."""
    config = {
        "url": "https://example.com",
        "ports": [80, 443],
        "extensions": [".php", ".html"],
        "max_tasks": 30,
        "crawl_depth": 2,
        "log_level": "INFO"
    }
    errors = validate_config(config)
    assert len(errors) == 0


def test_invalid_url_type():
    """Test that non-string URL is caught."""
    config = {"url": 123}
    errors = validate_config(config)
    assert any("url" in error.lower() for error in errors)


def test_invalid_port():
    """Test that invalid port numbers are caught."""
    config = {"ports": [80, 99999]}
    errors = validate_config(config)
    assert any("port" in error.lower() for error in errors)


def test_invalid_max_tasks():
    """Test that invalid max_tasks is caught."""
    config = {"max_tasks": -5}
    errors = validate_config(config)
    assert any("max_tasks" in error.lower() for error in errors)


def test_invalid_log_level():
    """Test that invalid log level is caught."""
    config = {"log_level": "INVALID"}
    errors = validate_config(config)
    assert any("log_level" in error.lower() for error in errors)


def test_empty_config():
    """Test that empty config is valid."""
    config = {}
    errors = validate_config(config)
    assert len(errors) == 0

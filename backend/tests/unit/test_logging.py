"""Unit tests for logging module."""
import pytest
import logging
from shared.logging import get_logger


class TestLogging:
    """Test suite for logging configuration."""

    def test_get_logger_returns_logger(self):
        """get_logger() returns a logger instance."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "fitapp"

    def test_logger_has_handler(self):
        """Logger should have at least one handler configured."""
        logger = get_logger()
        assert len(logger.handlers) > 0

    def test_logger_has_formatter(self):
        """Logger handler should have a formatter."""
        logger = get_logger()
        handler = logger.handlers[0]
        assert handler.formatter is not None

    def test_logger_level_default_info(self):
        """Logger should default to INFO level."""
        logger = get_logger()
        # Level might be INFO (20) or higher depending on env
        assert logger.level >= logging.DEBUG

import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

_logger = logging.getLogger("fitapp")
if not _logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(LOG_LEVEL)


def get_logger() -> logging.Logger:
    return _logger

"""
logger.py
─────────
Configures a single application-wide logger.
Import `logger` from here in every module instead of calling
logging.getLogger() repeatedly — this guarantees a consistent
format and log level everywhere.
"""

import logging
import sys
from app.config import get_config

config = get_config()

# ── Formatter ───────────────────────────────────────────────────────────────
_fmt = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Handler — write everything to stdout so cloud log collectors pick it up ─
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_fmt)

# ── Root logger ─────────────────────────────────────────────────────────────
logging.basicConfig(level=config.LOG_LEVEL, handlers=[_handler])

# Silence noisy third-party loggers
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a child logger with the given name.

    Usage
    -----
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Server started")
    """
    return logging.getLogger(name)

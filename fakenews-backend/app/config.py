"""
config.py
─────────
All application settings are read from environment variables (or a .env file).
Using a single Config object keeps the rest of the codebase free of os.getenv()
calls and makes it trivial to override values in tests or CI/CD pipelines.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file if it exists (no-op in production where env vars are injected directly)
load_dotenv()


class Config:
    # ── Server ──────────────────────────────────────────
    HOST: str  = os.getenv("HOST",  "0.0.0.0")
    PORT: int  = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"

    # ── Model artefacts ─────────────────────────────────
    MODEL_PATH:      str = os.getenv("MODEL_PATH",      "app/models/model.pkl")
    VECTORIZER_PATH: str = os.getenv("VECTORIZER_PATH", "app/models/vectorizer.pkl")

    # ── CORS ────────────────────────────────────────────
    # The env var holds a comma-separated string; we split it into a list.
    _raw_origins: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
    ALLOWED_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

    # ── Logging ─────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # ── Text constraints ────────────────────────────────
    MIN_TEXT_LENGTH: int = 10       # reject texts shorter than this
    MAX_TEXT_LENGTH: int = 50_000   # reject texts longer than this


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Return a cached singleton Config instance."""
    return Config()

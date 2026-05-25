"""
model_loader.py
───────────────
Handles loading (and caching) of the trained ML model and TF-IDF vectorizer.

Why a separate module?
  • Single Responsibility — one module owns all file-I/O for artefacts.
  • Startup fail-fast — if the files are missing the server refuses to start
    rather than crashing on the first request.
  • Cached singletons — model is loaded once at startup, not per-request.
"""

import pickle
from pathlib import Path
from typing  import Any

from app.config      import get_config
from app.utils.logger import get_logger

logger = get_logger(__name__)
config = get_config()


class ModelNotFoundError(RuntimeError):
    """Raised when a required model file is missing from disk."""


class ModelLoadError(RuntimeError):
    """Raised when a file exists but cannot be deserialized."""


def _load_pickle(path: str | Path, label: str) -> Any:
    """
    Load a single pickle file safely.

    Parameters
    ----------
    path  : Filesystem path to the .pkl file.
    label : Human-readable name used in log/error messages.

    Returns
    -------
    The deserialized Python object.
    """
    p = Path(path)

    if not p.exists():
        raise ModelNotFoundError(
            f"{label} not found at '{p.resolve()}'.\n"
            "Make sure you have placed your trained .pkl files inside app/models/\n"
            "and that MODEL_PATH / VECTORIZER_PATH in .env point to them."
        )

    try:
        with p.open("rb") as f:
            obj = pickle.load(f)                 # nosec — trusted internal files
        logger.info("Loaded %s from '%s'", label, p.resolve())
        return obj

    except (pickle.UnpicklingError, EOFError, ImportError, ModuleNotFoundError) as exc:
        raise ModelLoadError(
            f"Failed to deserialize {label} from '{p}': {exc}"
        ) from exc


# ── Module-level singletons ──────────────────────────────────────────────────
# These are populated once during application startup via load_artefacts().
_model:      Any = None
_vectorizer: Any = None


def load_artefacts() -> None:
    """
    Load model and vectorizer from disk and cache them in module globals.
    Called once inside the FastAPI lifespan context (startup event).
    Raises ModelNotFoundError or ModelLoadError on failure.
    """
    global _model, _vectorizer

    logger.info("Loading ML artefacts…")
    _model      = _load_pickle(config.MODEL_PATH,      "Classifier model")
    _vectorizer = _load_pickle(config.VECTORIZER_PATH, "TF-IDF vectorizer")
    logger.info("All artefacts loaded successfully.")


def get_model() -> Any:
    """Return the cached classifier. Raises RuntimeError if not yet loaded."""
    if _model is None:
        raise RuntimeError("Model has not been loaded. Did load_artefacts() run?")
    return _model


def get_vectorizer() -> Any:
    """Return the cached TF-IDF vectorizer. Raises RuntimeError if not yet loaded."""
    if _vectorizer is None:
        raise RuntimeError("Vectorizer has not been loaded. Did load_artefacts() run?")
    return _vectorizer

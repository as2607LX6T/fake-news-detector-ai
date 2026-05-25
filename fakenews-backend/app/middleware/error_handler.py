"""
error_handler.py
────────────────
Registers a single global exception handler so that every unhandled error
returns a consistent JSON body instead of an HTML traceback.

Response shape for all errors
──────────────────────────────
{
    "status":  "error",
    "code":    422,
    "message": "human-readable explanation",
    "detail":  "optional technical detail (omitted in production)"
}
"""

import traceback

from fastapi                  import Request, status
from fastapi.responses        import JSONResponse
from fastapi.exceptions       import RequestValidationError
from starlette.exceptions     import HTTPException as StarletteHTTPException

from app.utils.logger         import get_logger
from app.utils.model_loader   import ModelNotFoundError, ModelLoadError

logger = get_logger(__name__)


# ── Helper ───────────────────────────────────────────────────────────────────

def _error_body(code: int, message: str, detail: str | None = None) -> dict:
    body = {"status": "error", "code": code, "message": message}
    if detail:
        body["detail"] = detail
    return body


# ── Handlers ─────────────────────────────────────────────────────────────────

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning("HTTP %d — %s | path=%s", exc.status_code, exc.detail, request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, str(exc.detail)),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic input validation failed — 422 Unprocessable Entity."""
    errors = exc.errors()
    # Flatten Pydantic's verbose error list into one readable string
    messages = "; ".join(
        f"{' → '.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in errors
    )
    logger.warning("Validation error on %s: %s", request.url.path, messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body(422, "Input validation failed.", messages),
    )


async def model_not_found_handler(request: Request, exc: ModelNotFoundError):
    """Model .pkl file missing from disk."""
    logger.critical("Model file missing: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=_error_body(
            503,
            "The ML model is not available. Please contact the administrator.",
            str(exc),
        ),
    )


async def model_load_error_handler(request: Request, exc: ModelLoadError):
    """Model file exists but cannot be deserialized."""
    logger.critical("Model load error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=_error_body(
            503,
            "The ML model could not be loaded.",
            str(exc),
        ),
    )


async def value_error_handler(request: Request, exc: ValueError):
    logger.warning("ValueError on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=_error_body(400, str(exc)),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all — never let an internal stack trace leak to clients."""
    logger.error("Unhandled exception on %s:\n%s", request.url.path, traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body(
            500,
            "An unexpected error occurred. Please try again later.",
        ),
    )


# ── Registration helper ───────────────────────────────────────────────────────

def register_error_handlers(app) -> None:
    """Attach all handlers to the FastAPI application instance."""
    app.add_exception_handler(StarletteHTTPException,    http_exception_handler)
    app.add_exception_handler(RequestValidationError,    validation_exception_handler)
    app.add_exception_handler(ModelNotFoundError,        model_not_found_handler)
    app.add_exception_handler(ModelLoadError,            model_load_error_handler)
    app.add_exception_handler(ValueError,                value_error_handler)
    app.add_exception_handler(Exception,                 generic_exception_handler)

"""
health.py
─────────
Health check endpoints used by:
  • Load balancers  (GET /health)
  • Render / Railway startup checks
  • Monitoring dashboards
  • Frontend "is backend alive?" pings

GET /health         — lightweight liveness probe (always fast)
GET /health/ready   — readiness probe (checks model is loaded)
"""

from fastapi        import APIRouter
from pydantic       import BaseModel

from app.utils.model_loader import get_model, get_vectorizer
from app.utils.logger       import get_logger

router = APIRouter(prefix="/health", tags=["Health"])
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    status:  str
    message: str


class ReadyResponse(BaseModel):
    status:     str
    model:      bool
    vectorizer: bool
    message:    str


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns 200 OK immediately. Used by load balancers.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", message="TruthLens API is running.")


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness probe",
    description="Returns 200 only when the ML model and vectorizer are loaded.",
)
async def readiness_check() -> ReadyResponse:
    model_ok = False
    vec_ok   = False

    try:
        get_model()
        model_ok = True
    except RuntimeError:
        pass

    try:
        get_vectorizer()
        vec_ok = True
    except RuntimeError:
        pass

    ready = model_ok and vec_ok

    logger.debug("Readiness: model=%s vectorizer=%s", model_ok, vec_ok)

    return ReadyResponse(
        status="ready" if ready else "not_ready",
        model=model_ok,
        vectorizer=vec_ok,
        message="All systems operational." if ready else "ML artefacts not loaded yet.",
    )

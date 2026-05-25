"""
main.py
───────
Application factory — creates and configures the FastAPI instance.

What happens here
─────────────────
1.  lifespan context:  loads ML artefacts ONCE at startup (fail-fast if missing)
2.  CORS middleware:   allows the React frontend to call us from a different port
3.  Error handlers:    all unhandled exceptions return clean JSON (never HTML)
4.  Routers:          /predict  and  /health  are registered here
5.  Root redirect:    GET /  →  /docs  (convenience for new developers)
"""

from contextlib          import asynccontextmanager

from fastapi             import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses   import RedirectResponse

from app.config          import get_config
from app.utils.logger    import get_logger
from app.utils.model_loader import load_artefacts
from app.middleware.error_handler import register_error_handlers
from app.routes          import predict, health

config = get_config()
logger = get_logger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────
# FastAPI's lifespan replaces the deprecated @app.on_event("startup") pattern.
# Code before `yield` runs on startup; code after `yield` runs on shutdown.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    logger.info("=" * 60)
    logger.info("  TruthLens Fake News Detection API — Starting up")
    logger.info("=" * 60)

    load_artefacts()          # will raise and abort startup if files are missing

    logger.info("Server ready. Docs available at  http://localhost:%d/docs", config.PORT)
    logger.info("=" * 60)

    yield  # ← application runs here

    # ── Shutdown ──
    logger.info("Server shutting down. Goodbye.")


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="TruthLens — Fake News Detection API",
        description=(
            "REST API that accepts a news article or headline and returns "
            "a **Fake / Real** verdict with a confidence score and risk level."
        ),
        version="1.0.0",
        contact={
            "name":  "TruthLens Team",
            "email": "hello@truthlens.ai",
        },
        license_info={"name": "MIT"},
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    # This lets the React frontend (running on localhost:5173) call the API.
    # In production, replace "*" / dev origins with your actual domain.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global error handlers ─────────────────────────────────────────────────
    register_error_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(predict.router)

    # ── Root redirect → interactive docs ──────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    return app


# Instantiate once — imported by uvicorn as  "app.main:app"
app = create_app()

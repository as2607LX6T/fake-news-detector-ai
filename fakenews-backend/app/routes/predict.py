"""
predict.py
──────────
POST /predict — The core endpoint.

Request body
────────────
{
    "text": "Full article or headline text here…"
}

Response body (200 OK)
──────────────────────
{
    "status":     "success",
    "prediction": "Fake",
    "confidence": "93.4%",
    "risk":       "HIGH",
    "word_count": 128
}

Error responses follow the global error handler shape.
"""

from fastapi           import APIRouter
from pydantic          import BaseModel, Field, field_validator

from app.config        import get_config
from app.utils.predictor import predict
from app.utils.logger  import get_logger

router = get_logger(__name__)          # just for naming; real router below
logger = get_logger(__name__)
config = get_config()

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """
    Schema for the incoming prediction request.
    Pydantic automatically validates types and runs our custom validators.
    """
    text: str = Field(
        ...,                                  # required — no default
        description="News article or headline to analyse.",
        examples=["Scientists discover water on Mars — NASA confirms in secret memo."],
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if len(v) < config.MIN_TEXT_LENGTH:
            raise ValueError(
                f"Text is too short. Minimum {config.MIN_TEXT_LENGTH} characters required."
            )
        if len(v) > config.MAX_TEXT_LENGTH:
            raise ValueError(
                f"Text is too long. Maximum {config.MAX_TEXT_LENGTH:,} characters allowed."
            )
        return v


class PredictResponse(BaseModel):
    """Response schema — documents the API shape in the auto-generated docs."""
    status:     str   = Field(..., examples=["success"])
    prediction: str   = Field(..., examples=["Fake"])
    confidence: str   = Field(..., examples=["93.4%"])
    risk:       str   = Field(..., examples=["HIGH"])
    word_count: int   = Field(..., examples=[128])


# ── Route ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=PredictResponse,
    summary="Detect fake news",
    description=(
        "Submit a news article or headline. "
        "Returns a **Fake / Real** verdict, a confidence percentage, "
        "and a risk level (LOW / MEDIUM / HIGH)."
    ),
    responses={
        400: {"description": "Input validation error"},
        422: {"description": "Request schema error"},
        503: {"description": "ML model unavailable"},
    },
)
async def predict_news(body: PredictRequest) -> PredictResponse:
    """
    Core prediction endpoint.

    The route itself is intentionally thin:
      1. Accept validated input from Pydantic
      2. Delegate to predictor.predict()
      3. Format and return the response
    """
    word_count = len(body.text.split())
    logger.info("Received prediction request | word_count=%d", word_count)

    result = predict(body.text)          # all ML logic lives in predictor.py

    return PredictResponse(
        status="success",
        prediction=result.prediction,
        confidence=f"{result.confidence}%",
        risk=result.risk,
        word_count=word_count,
    )

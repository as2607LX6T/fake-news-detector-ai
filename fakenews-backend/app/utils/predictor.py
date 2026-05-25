"""
predictor.py
────────────
Core prediction logic — takes cleaned text and returns a structured result.

Why separate from the route?
  • Routes only deal with HTTP (request → response).
  • This module deals with ML (text → prediction).
  • Makes it trivial to call from tests without spinning up an HTTP server.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass

from app.utils.model_loader   import get_model, get_vectorizer
from app.utils.text_processor import clean_text
from app.utils.logger         import get_logger

logger = get_logger(__name__)


# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class PredictionResult:
    prediction:  str    # "Fake" or "Real"
    confidence:  float  # 0.0 – 100.0
    risk:        str    # "LOW" | "MEDIUM" | "HIGH"
    label_index: int    # raw integer label from the model (0 or 1)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _map_risk(confidence: float, prediction: str) -> str:
    """
    Derive a human-readable risk level.

    Rules
    -----
    • Fake + high confidence  → HIGH risk
    • Fake + medium confidence → MEDIUM risk
    • Fake + low confidence   → MEDIUM risk  (uncertain fake is still risky)
    • Real + any confidence   → LOW risk
    """
    if prediction == "Real":
        return "LOW"
    if confidence >= 85:
        return "HIGH"
    return "MEDIUM"


# ── Public API ───────────────────────────────────────────────────────────────

def predict(raw_text: str) -> PredictionResult:
    """
    Full prediction pipeline:
      raw text → clean → vectorize → classify → result

    Parameters
    ----------
    raw_text : The original user-submitted text (not yet cleaned).

    Returns
    -------
    PredictionResult dataclass with prediction, confidence, and risk.

    Raises
    ------
    ValueError   — if cleaned text is empty after preprocessing.
    RuntimeError — if model/vectorizer not loaded (should never happen in prod).
    """

    # Step 1 ─ Preprocess
    cleaned = clean_text(raw_text)
    if not cleaned.strip():
        raise ValueError(
            "Text became empty after preprocessing. "
            "Please submit a longer, more descriptive passage."
        )

    logger.debug("Cleaned text (first 120 chars): %s", cleaned[:120])

    # Step 2 ─ Vectorize  (returns a sparse matrix of shape [1, vocab_size])
    model      = get_model()
    vectorizer = get_vectorizer()
    features   = vectorizer.transform([cleaned])

    # Step 3 ─ Predict class label
    label_index: int = int(model.predict(features)[0])

    # Step 4 ─ Confidence score
    # predict_proba returns [[prob_class_0, prob_class_1]]
    # If the model does not support predict_proba (e.g. LinearSVC),
    # we fall back to a fixed 0.5 and log a warning.
    if hasattr(model, "predict_proba"):
        proba      = model.predict_proba(features)[0]           # shape: (n_classes,)
        confidence = float(np.max(proba)) * 100                 # highest class prob → %
    elif hasattr(model, "decision_function"):
        # LinearSVC — convert decision score to a 0–100 proxy via sigmoid
        score      = model.decision_function(features)[0]
        confidence = float(1 / (1 + np.exp(-score))) * 100
    else:
        logger.warning("Model has neither predict_proba nor decision_function. "
                       "Confidence will be reported as 50%%.")
        confidence = 50.0

    # Step 5 ─ Map label index to human label
    # Convention: 0 = Fake, 1 = Real  (matches most public fake-news datasets)
    # If your dataset uses the opposite convention, swap the mapping below.
    prediction = "Real" if label_index == 1 else "Fake"

    risk = _map_risk(confidence, prediction)

    logger.info(
        "Prediction: %s | Confidence: %.1f%% | Risk: %s | Label index: %d",
        prediction, confidence, risk, label_index,
    )

    return PredictionResult(
        prediction=prediction,
        confidence=round(confidence, 1),
        risk=risk,
        label_index=label_index,
    )

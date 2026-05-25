"""
=============================================================================
predict.py — Inference Module for Fake News Detection
=============================================================================

PURPOSE:
    Load saved model + vectoriser from disk and provide a clean API for
    making predictions on new, unseen articles.

    This is the module you'd expose via a Flask/FastAPI endpoint in production.

USAGE:
    from src.predict import FakeNewsPredictor

    predictor = FakeNewsPredictor()
    result = predictor.predict("Scientists discover that the earth is flat!")
    print(result)
    # {'label': 0, 'verdict': 'FAKE', 'confidence': 0.97, 'cleaned_text': '...'}

Author: AI/ML Engineer
=============================================================================
"""

import sys
import logging
import pickle
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocess import clean_text  # noqa: E402

logger = logging.getLogger(__name__)

MODELS_DIR = PROJECT_ROOT / "models"


class FakeNewsPredictor:
    """
    Encapsulates model loading and inference in a clean, reusable class.

    Design pattern: Lazy loading — artefacts are loaded from disk only
    once (on first call to predict) and then cached as instance attributes.
    This avoids the overhead of disk I/O on every prediction when the
    predictor is used in a long-running server process.

    Attributes:
        model      : The loaded sklearn estimator.
        vectorizer : The loaded TfidfVectorizer.
        metadata   : Training metadata dict (accuracy, config, etc.)
    """

    def __init__(
        self,
        model_path: Path = MODELS_DIR / "best_model.pkl",
        vectorizer_path: Path = MODELS_DIR / "tfidf_vectorizer.pkl",
        metadata_path: Path = MODELS_DIR / "training_metadata.pkl",
    ):
        self.model_path      = Path(model_path)
        self.vectorizer_path = Path(vectorizer_path)
        self.metadata_path   = Path(metadata_path)

        self.model      = None
        self.vectorizer = None
        self.metadata   = None

        # Load immediately on construction so errors surface early
        self._load_artifacts()

    # ── Private helpers ───────────────────────────────────────────────────

    def _load_artifact(self, path: Path, label: str):
        """Load and return a pickled object."""
        if not path.exists():
            raise FileNotFoundError(
                f"{label} not found at '{path}'.\n"
                f"Run train.py first to generate saved models."
            )
        with open(path, "rb") as f:
            obj = pickle.load(f)
        logger.debug(f"Loaded {label} from {path}")
        return obj

    def _load_artifacts(self) -> None:
        """Load all three artefacts in one call."""
        logger.info("Loading model artefacts …")
        self.model      = self._load_artifact(self.model_path,      "Best Model")
        self.vectorizer = self._load_artifact(self.vectorizer_path, "TF-IDF Vectoriser")

        if self.metadata_path.exists():
            self.metadata = self._load_artifact(self.metadata_path, "Training Metadata")
            logger.info(
                f"  Model : {self.metadata.get('best_model_name', 'Unknown')}"
                f"  |  Test accuracy : {self.metadata.get('best_accuracy', 0):.4f}"
            )

    # ── Public API ────────────────────────────────────────────────────────

    def predict(self, text: str) -> dict:
        """
        Predict whether a news article is Fake or Real.

        Args:
            text (str): Raw article text. Can be title + body concatenated.

        Returns:
            dict: {
                "label":        int,   # 0 = Fake, 1 = Real
                "verdict":      str,   # "FAKE" or "REAL"
                "confidence":   float, # Probability of the predicted class
                "cleaned_text": str,   # Preprocessed version (for debugging)
            }
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        # Preprocess
        cleaned = clean_text(text)
        if not cleaned.strip():
            raise ValueError("After preprocessing, the text became empty. Try a longer article.")

        # Vectorise
        features = self.vectorizer.transform([cleaned])

        # Predict
        label = int(self.model.predict(features)[0])
        confidence = self._get_confidence(features, label)

        return {
            "label":        label,
            "verdict":      "REAL" if label == 1 else "FAKE",
            "confidence":   round(confidence, 4),
            "cleaned_text": cleaned,
        }

    def predict_batch(self, texts: list[str]) -> list[dict]:
        """
        Predict a list of articles efficiently in a single vectoriser call.

        Args:
            texts (list[str]): List of raw article strings.

        Returns:
            list[dict]: One result dict per input article.
        """
        if not texts:
            return []

        # Preprocess all texts
        cleaned_texts = [clean_text(t) for t in texts]

        # Vectorise in one shot (much faster than looping)
        features = self.vectorizer.transform(cleaned_texts)

        # Predict
        labels = self.model.predict(features).tolist()

        results = []
        for i, (label, cleaned) in enumerate(zip(labels, cleaned_texts)):
            conf = self._get_confidence(features[i], label)
            results.append({
                "label":        int(label),
                "verdict":      "REAL" if label == 1 else "FAKE",
                "confidence":   round(conf, 4),
                "cleaned_text": cleaned,
            })
        return results

    def _get_confidence(self, features, label: int) -> float:
        """
        Extract prediction confidence from the model.

        Different sklearn models expose confidence differently:
            - Models with predict_proba(): return class probability directly.
            - Models with decision_function(): convert raw score with sigmoid.
        """
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(features)[0]
            return float(proba[label])
        elif hasattr(self.model, "decision_function"):
            score = float(self.model.decision_function(features)[0])
            # Sigmoid maps any real number to (0, 1)
            return float(1 / (1 + np.exp(-abs(score))))
        else:
            return 1.0  # Fallback if neither method exists

    def model_info(self) -> dict:
        """Return a summary of the loaded model and training configuration."""
        if self.metadata:
            return self.metadata
        return {
            "model_type": type(self.model).__name__,
            "vectorizer_type": type(self.vectorizer).__name__,
        }


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    predictor = FakeNewsPredictor()

    print("\n" + "=" * 65)
    print("  FAKE NEWS DETECTOR — INFERENCE DEMO")
    print("=" * 65)

    test_articles = [
        (
            "NASA scientists confirm moon is made of cheese after new probe analysis",
            "Expected: FAKE"
        ),
        (
            "Federal Reserve raises interest rates by 25 basis points amid inflation concerns",
            "Expected: REAL"
        ),
        (
            "SHOCKING: Government secretly putting mind-control chemicals in water supply!!!",
            "Expected: FAKE"
        ),
        (
            "Senate committee approves $500 billion climate spending package after months of debate",
            "Expected: REAL"
        ),
    ]

    for article, expected in test_articles:
        result = predictor.predict(article)
        icon = "✓" if result["verdict"] in expected else "✗"
        print(f"\n  {icon} Article    : {article[:75]}…")
        print(f"    Verdict    : {result['verdict']}")
        print(f"    Confidence : {result['confidence']:.2%}")
        print(f"    ({expected})")

    print("\n" + "=" * 65)
    print("  Model Info:")
    for k, v in predictor.model_info().items():
        print(f"    {k}: {v}")
    print("=" * 65 + "\n")

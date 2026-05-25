"""
=============================================================================
train.py — Model Training Pipeline for Fake News Detection
=============================================================================

PURPOSE:
    Orchestrates the end-to-end ML pipeline:
        Load data → Preprocess → Vectorise → Train → Evaluate → Save

WHY THREE MODELS?
    No single algorithm is universally best. We train three and pick the
    winner based on validation accuracy. Here's the reasoning:

    ┌──────────────────────────────┬────────────────────────────────────────┐
    │ Algorithm                    │ Why It's a Good Fit Here               │
    ├──────────────────────────────┼────────────────────────────────────────┤
    │ Logistic Regression          │ Strong baseline for text classification.│
    │                              │ Fast, interpretable, works well with    │
    │                              │ high-dimensional TF-IDF features.       │
    ├──────────────────────────────┼────────────────────────────────────────┤
    │ PassiveAggressiveClassifier  │ Online learning algorithm designed for  │
    │                              │ large-scale text classification. Very    │
    │                              │ efficient with sparse TF-IDF matrices.  │
    ├──────────────────────────────┼────────────────────────────────────────┤
    │ Multinomial Naive Bayes      │ Probabilistic model assuming feature     │
    │                              │ independence. Surprisingly effective for │
    │                              │ text due to word-frequency patterns.     │
    └──────────────────────────────┴────────────────────────────────────────┘

WHAT IS TF-IDF? (explained simply)
    TF-IDF = Term Frequency × Inverse Document Frequency

    • TF  (Term Frequency):  How often does a word appear in THIS article?
                              "corona" appearing 10 times → high TF.
    • IDF (Inverse Doc Freq): How RARE is this word across ALL articles?
                              "the" appears everywhere → low IDF (penalised).
                              "hydroxychloroquine" is rare → high IDF (rewarded).

    The product rewards words that are FREQUENT in one article but RARE
    across the corpus — exactly the kind of distinctive vocabulary that
    separates real journalism from fabricated content.

Author: AI/ML Engineer
=============================================================================
"""

import os
import sys
import time
import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ---------------------------------------------------------------------------
# Ensure src/ is on the Python path (so we can import our own modules)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocess import load_and_merge_datasets, preprocess_dataframe  # noqa: E402
from evaluate import evaluate_model, compare_models                    # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths (all relative to the project root so the project is portable)
# ---------------------------------------------------------------------------
DATA_DIR   = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

FAKE_CSV   = DATA_DIR / "Fake.csv"
TRUE_CSV   = DATA_DIR / "True.csv"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# TF-IDF configuration
# ---------------------------------------------------------------------------
TFIDF_CONFIG = {
    # max_features: Keep only the top N words by corpus frequency.
    # More features = more signal but slower training. 50,000 is a good sweet spot.
    "max_features": 50_000,

    # ngram_range: (1,2) means use single words AND two-word phrases.
    # "fake news" as a bigram is more informative than "fake" and "news" alone.
    "ngram_range": (1, 2),

    # sublinear_tf: Apply log(1 + tf) instead of raw tf.
    # Prevents extremely common words from dominating just because they appear
    # 100 times instead of 10 times.
    "sublinear_tf": True,

    # min_df: Ignore words that appear in fewer than 2 documents.
    # Removes typos and ultra-rare tokens that can't generalise.
    "min_df": 2,
}


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------
def build_models() -> dict:
    """
    Return a dictionary of untrained scikit-learn classifier instances.

    Keeping models in a dict lets us iterate over them cleanly —
    train, evaluate, and compare without copy-pasting code.

    Returns:
        dict[str, estimator]: Named classifiers ready to be fitted.
    """
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,     # Increase iterations to ensure convergence
            C=1.0,             # Regularisation strength (lower = more regularised)
            solver="lbfgs",    # Efficient solver for medium-sized datasets
            n_jobs=-1,         # Use all CPU cores
            random_state=42,
        ),
        "Passive Aggressive Classifier": PassiveAggressiveClassifier(
            max_iter=50,
            C=1.0,
            random_state=42,
            n_jobs=-1,
        ),
        "Multinomial Naive Bayes": MultinomialNB(
            alpha=0.1,         # Laplace smoothing (avoids zero probability)
        ),
    }


# ---------------------------------------------------------------------------
# Saving / loading helpers
# ---------------------------------------------------------------------------
def save_artifact(obj, filepath: Path, label: str) -> None:
    """
    Pickle an object to disk with error handling and logging.

    WHY PICKLE?
        Pickle serialises any Python object to bytes so it can be reloaded
        later without retraining. The vectoriser and model must be saved
        SEPARATELY because:
        • The vectoriser holds the vocabulary (word → column index mapping).
        • The model holds the learned weights.
        Both are needed at inference time.

    Args:
        obj:      Any picklable Python object (model, vectoriser, dict …).
        filepath: Destination path (Path object).
        label:    Human-readable name for log messages.
    """
    try:
        with open(filepath, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        size_kb = filepath.stat().st_size / 1024
        logger.info(f"  Saved {label} → {filepath}  ({size_kb:.1f} KB)")
    except Exception as e:
        logger.error(f"Failed to save {label}: {e}")
        raise


def load_artifact(filepath: Path, label: str):
    """
    Load a pickled object from disk.

    Args:
        filepath: Source path (Path object).
        label:    Human-readable name for log messages.

    Returns:
        The deserialised Python object.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"{label} not found at {filepath}")
    with open(filepath, "rb") as f:
        obj = pickle.load(f)
    logger.info(f"  Loaded {label} ← {filepath}")
    return obj


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------
def train_pipeline(
    fake_csv: Path = FAKE_CSV,
    true_csv: Path = TRUE_CSV,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Run the complete training pipeline end-to-end.

    Steps:
        1.  Load & merge datasets
        2.  NLP preprocessing
        3.  Train/test split
        4.  TF-IDF vectorisation
        5.  Train all three models
        6.  Evaluate each model
        7.  Select & save the best model
        8.  Save the vectoriser
        9.  Return a results summary

    Args:
        fake_csv     : Path to Fake.csv
        true_csv     : Path to True.csv
        test_size    : Fraction of data held out for testing (default 20 %)
        random_state : Seed for reproducibility

    Returns:
        dict: {
            "best_model_name": str,
            "best_accuracy":   float,
            "results":         dict[str, dict],  # per-model metrics
            "vectorizer":      TfidfVectorizer,
            "best_model":      estimator,
        }
    """
    pipeline_start = time.time()
    logger.info("=" * 65)
    logger.info("  FAKE NEWS DETECTION — TRAINING PIPELINE")
    logger.info("=" * 65)

    # ── 1. Load & merge ───────────────────────────────────────────────────
    logger.info("\n[1/7] Loading and merging datasets …")
    df = load_and_merge_datasets(str(fake_csv), str(true_csv))

    # ── 2. NLP preprocessing ──────────────────────────────────────────────
    logger.info("\n[2/7] Applying NLP preprocessing …")
    df = preprocess_dataframe(df, text_col="content")

    # ── 3. Train / test split ─────────────────────────────────────────────
    logger.info(f"\n[3/7] Splitting data (test_size={test_size}) …")
    X = df["cleaned_text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,          # Ensures both splits have the same label ratio
    )
    logger.info(f"  Training set : {len(X_train):,} samples")
    logger.info(f"  Test set     : {len(X_test):,} samples")

    # ── 4. TF-IDF vectorisation ───────────────────────────────────────────
    logger.info("\n[4/7] Fitting TF-IDF vectoriser …")
    vectorizer = TfidfVectorizer(**TFIDF_CONFIG)

    # CRITICAL: fit ONLY on training data to prevent data leakage.
    # Data leakage = the model "sees" test data during training, making
    # evaluation metrics falsely optimistic.
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf  = vectorizer.transform(X_test)   # transform only (no fit)

    vocab_size = len(vectorizer.vocabulary_)
    logger.info(f"  Vocabulary size : {vocab_size:,} tokens")
    logger.info(f"  Matrix shape    : {X_train_tfidf.shape}")

    # ── 5. Train all models ───────────────────────────────────────────────
    logger.info("\n[5/7] Training models …")
    models    = build_models()
    results   = {}
    trained   = {}

    for name, model in models.items():
        logger.info(f"  ▶ Training {name} …")
        t0 = time.time()
        model.fit(X_train_tfidf, y_train)
        elapsed = time.time() - t0
        logger.info(f"    Done in {elapsed:.2f}s")
        trained[name] = model

    # ── 6. Evaluate all models ────────────────────────────────────────────
    logger.info("\n[6/7] Evaluating models …")
    for name, model in trained.items():
        metrics = evaluate_model(
            model, X_test_tfidf, y_test,
            model_name=name,
            report_dir=REPORTS_DIR,
        )
        results[name] = metrics

    # ── 7. Select best model ──────────────────────────────────────────────
    logger.info("\n[7/7] Selecting and saving best model …")
    best_name = max(results, key=lambda n: results[n]["accuracy"])
    best_model = trained[best_name]
    best_acc   = results[best_name]["accuracy"]

    logger.info(f"\n  ★  Best model : {best_name}")
    logger.info(f"  ★  Accuracy   : {best_acc:.4f}  ({best_acc*100:.2f} %)")

    # Save artefacts
    save_artifact(best_model,  MODELS_DIR / "best_model.pkl",    "Best Model")
    save_artifact(vectorizer,  MODELS_DIR / "tfidf_vectorizer.pkl", "TF-IDF Vectoriser")

    # Save metadata (model name, accuracy, config) as a lightweight record
    metadata = {
        "best_model_name": best_name,
        "best_accuracy":   best_acc,
        "tfidf_config":    TFIDF_CONFIG,
        "test_size":       test_size,
        "train_samples":   len(X_train),
        "test_samples":    len(X_test),
        "vocab_size":      vocab_size,
    }
    save_artifact(metadata, MODELS_DIR / "training_metadata.pkl", "Training Metadata")

    # Print final comparison table
    compare_models(results)

    total_time = time.time() - pipeline_start
    logger.info(f"\n  Pipeline completed in {total_time:.1f}s")
    logger.info("=" * 65)

    return {
        "best_model_name": best_name,
        "best_accuracy":   best_acc,
        "results":         results,
        "vectorizer":      vectorizer,
        "best_model":      best_model,
    }


# ---------------------------------------------------------------------------
# Inference helper (load saved model and predict new articles)
# ---------------------------------------------------------------------------
def predict_article(text: str) -> dict:
    """
    Predict whether a single news article is Fake or Real.

    Loads the saved model and vectoriser from disk, applies the same
    preprocessing used during training, and returns a prediction.

    Args:
        text (str): Raw article text (title + body recommended).

    Returns:
        dict: {
            "label":       int   (0 = Fake, 1 = Real),
            "verdict":     str   ("FAKE" or "REAL"),
            "confidence":  float (probability of the predicted class),
        }

    Usage:
        result = predict_article("Scientists confirm moon landing was faked!")
        print(result)
        # {'label': 0, 'verdict': 'FAKE', 'confidence': 0.97}
    """
    # ── Load artefacts ────────────────────────────────────────────────────
    model      = load_artifact(MODELS_DIR / "best_model.pkl",       "Best Model")
    vectorizer = load_artifact(MODELS_DIR / "tfidf_vectorizer.pkl", "Vectoriser")

    # ── Preprocess ────────────────────────────────────────────────────────
    # Import here to avoid circular import at module level
    from preprocess import clean_text
    cleaned = clean_text(text)

    # ── Vectorise ─────────────────────────────────────────────────────────
    features = vectorizer.transform([cleaned])

    # ── Predict ───────────────────────────────────────────────────────────
    label = int(model.predict(features)[0])

    # Confidence: probability of the predicted class (if model supports it)
    if hasattr(model, "predict_proba"):
        confidence = float(model.predict_proba(features)[0][label])
    else:
        # PassiveAggressiveClassifier uses decision_function instead
        score = float(model.decision_function(features)[0])
        # Convert raw score to an approximate confidence using sigmoid
        confidence = float(1 / (1 + np.exp(-abs(score))))

    return {
        "label":      label,
        "verdict":    "REAL" if label == 1 else "FAKE",
        "confidence": round(confidence, 4),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Check that data files exist before starting
    missing = [p for p in [FAKE_CSV, TRUE_CSV] if not p.exists()]
    if missing:
        logger.error(
            f"Missing data files: {[str(p) for p in missing]}\n"
            f"Please place Fake.csv and True.csv inside the 'data/' directory."
        )
        sys.exit(1)

    # Run the full pipeline
    output = train_pipeline()

    # Quick demo prediction using the freshly saved model
    logger.info("\n=== Quick Inference Demo ===")
    sample_texts = [
        "NASA confirms humans have never landed on the moon. All footage was staged in Hollywood.",
        "Congress passed a bipartisan infrastructure bill worth $1.2 trillion on Tuesday.",
    ]
    for sample in sample_texts:
        result = predict_article(sample)
        print(f"\n  Article : {sample[:80]}…")
        print(f"  Verdict : {result['verdict']}  (confidence: {result['confidence']:.2%})")

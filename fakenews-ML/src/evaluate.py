"""
=============================================================================
evaluate.py — Model Evaluation Suite for Fake News Detection
=============================================================================

PURPOSE:
    Provides functions to rigorously evaluate trained classifiers and
    produce human-readable reports, confusion matrix plots, and comparison
    tables.

WHY ACCURACY ALONE ISN'T ENOUGH:
    If 90 % of articles are real and a model labels everything as "real",
    it gets 90 % accuracy but is completely useless — it never catches fake
    news. That's why we also report:

    • Precision  : Of all articles flagged as fake, what fraction truly are?
                   (Low precision → many false alarms)
    • Recall     : Of all actual fake articles, what fraction did we catch?
                   (Low recall → we miss many fakes — dangerous!)
    • F1-Score   : Harmonic mean of precision and recall. Good single metric
                   when classes are imbalanced.
    • Confusion Matrix : Visual breakdown of TP/TN/FP/FN counts.

Author: AI/ML Engineer
=============================================================================
"""

import logging
from pathlib import Path
from typing import Any

import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend (safe for servers)
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# Class labels used in reports and plots
CLASS_NAMES = ["Fake (0)", "Real (1)"]


# ---------------------------------------------------------------------------
def evaluate_model(
    model: Any,
    X_test,
    y_test,
    model_name: str = "Model",
    report_dir: Path = Path("reports"),
) -> dict:
    """
    Evaluate a trained classifier and persist reports to disk.

    This function:
        1. Generates predictions on the test set
        2. Computes accuracy, precision, recall, F1
        3. Prints a classification report to the console
        4. Saves a confusion matrix PNG
        5. Saves the classification report as a .txt file

    Args:
        model      : Fitted scikit-learn estimator.
        X_test     : TF-IDF feature matrix for the test set (sparse).
        y_test     : True labels for the test set.
        model_name : Human-readable name (used in filenames & plot titles).
        report_dir : Directory where report files are saved.

    Returns:
        dict: {
            "accuracy":            float,
            "classification_report": str,
            "confusion_matrix":    np.ndarray,
        }
    """
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    # ── Predictions ───────────────────────────────────────────────────────
    y_pred = model.predict(X_test)

    # ── Accuracy ──────────────────────────────────────────────────────────
    acc = accuracy_score(y_test, y_pred)

    # ── Classification Report ─────────────────────────────────────────────
    report = classification_report(
        y_test, y_pred,
        target_names=CLASS_NAMES,
        digits=4,              # Show 4 decimal places for precision
    )

    # ── Confusion Matrix ──────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)

    # Print to console
    separator = "─" * 55
    print(f"\n{separator}")
    print(f"  {model_name}")
    print(separator)
    print(f"  Accuracy : {acc:.4f}  ({acc*100:.2f} %)")
    print(f"\n  Classification Report:\n")
    print(report)

    # ── Save confusion matrix plot ─────────────────────────────────────────
    _save_confusion_matrix(cm, model_name, report_dir)

    # ── Save classification report ─────────────────────────────────────────
    safe_name = model_name.lower().replace(" ", "_")
    report_path = report_dir / f"{safe_name}_report.txt"
    with open(report_path, "w") as f:
        f.write(f"Model: {model_name}\n")
        f.write(f"Accuracy: {acc:.6f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\n\nConfusion Matrix:\n")
        f.write(str(cm))
    logger.info(f"  Report saved → {report_path}")

    return {
        "accuracy":              acc,
        "classification_report": report,
        "confusion_matrix":      cm,
    }


# ---------------------------------------------------------------------------
def _save_confusion_matrix(cm: np.ndarray, model_name: str, report_dir: Path) -> None:
    """
    Render and save a styled confusion matrix heatmap.

    READING THE CONFUSION MATRIX:
                        Predicted Fake    Predicted Real
        Actual Fake  [  True Negative   |  False Positive  ]
        Actual Real  [  False Negative  |  True Positive   ]

        • True Negative  (TN): Correctly flagged as fake ✓
        • True Positive  (TP): Correctly identified as real ✓
        • False Positive (FP): Real news incorrectly called fake (type I error)
        • False Negative (FN): Fake news that slipped through (type II error) ← dangerous

    Args:
        cm         : 2×2 confusion matrix array.
        model_name : Used in the plot title and filename.
        report_dir : Directory to save the PNG.
    """
    safe_name = model_name.lower().replace(" ", "_")
    fig_path = report_dir / f"{safe_name}_confusion_matrix.png"

    fig, ax = plt.subplots(figsize=(7, 6))

    # Colour map: Blues for correct predictions
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",                    # Show integers (not scientific notation)
        cmap="Blues",
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        linewidths=0.5,
        linecolor="lightgray",
        ax=ax,
        annot_kws={"size": 14, "weight": "bold"},
    )

    ax.set_title(f"Confusion Matrix — {model_name}", fontsize=14, pad=15)
    ax.set_ylabel("Actual Label",    fontsize=12)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    logger.info(f"  Confusion matrix saved → {fig_path}")


# ---------------------------------------------------------------------------
def compare_models(results: dict) -> None:
    """
    Print a formatted comparison table of all models sorted by accuracy.

    Args:
        results (dict): Output from evaluate_model() keyed by model name.
                        Each value must contain at least {"accuracy": float}.
    """
    print("\n" + "=" * 55)
    print("  MODEL COMPARISON — RANKED BY ACCURACY")
    print("=" * 55)
    print(f"  {'Rank':<6} {'Model':<35} {'Accuracy':>10}")
    print("  " + "-" * 53)

    sorted_models = sorted(results.items(), key=lambda x: x[1]["accuracy"], reverse=True)

    for rank, (name, metrics) in enumerate(sorted_models, start=1):
        acc   = metrics["accuracy"]
        medal = "★" if rank == 1 else " "
        print(f"  {medal} {rank:<5} {name:<35} {acc:.4f}  ({acc*100:.2f} %)")

    print("=" * 55)
    best_name = sorted_models[0][0]
    best_acc  = sorted_models[0][1]["accuracy"]
    print(f"\n  Winner → {best_name}  ({best_acc*100:.2f} %)\n")


# ---------------------------------------------------------------------------
def save_accuracy_bar_chart(results: dict, report_dir: Path = Path("reports")) -> None:
    """
    Save a horizontal bar chart comparing model accuracies.

    Args:
        results    : Same dict as passed to compare_models().
        report_dir : Where to save 'model_comparison.png'.
    """
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    names = list(results.keys())
    accs  = [results[n]["accuracy"] * 100 for n in names]

    # Shorten names for readability in the chart
    short_names = [n.replace(" Classifier", "") for n in names]

    fig, ax = plt.subplots(figsize=(9, 4))

    colours = ["#2196F3", "#4CAF50", "#FF9800"]
    bars = ax.barh(short_names, accs, color=colours[:len(names)], edgecolor="white", height=0.5)

    # Annotate bars with exact accuracy values
    for bar, acc in zip(bars, accs):
        ax.text(
            bar.get_width() - 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{acc:.2f} %",
            va="center", ha="right",
            color="white", fontweight="bold", fontsize=11,
        )

    ax.set_xlim(min(accs) - 2, 101)
    ax.set_xlabel("Accuracy (%)", fontsize=12)
    ax.set_title("Model Accuracy Comparison", fontsize=14, pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    chart_path = report_dir / "model_comparison.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    logger.info(f"  Accuracy bar chart saved → {chart_path}")

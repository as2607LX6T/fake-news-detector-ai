"""
=============================================================================
preprocess.py — NLP Preprocessing Pipeline for Fake News Detection
=============================================================================

PURPOSE:
    This module handles ALL text cleaning and transformation steps before
    feeding data into any machine learning model. Clean data = better models.

WHY PREPROCESSING MATTERS:
    Raw news text contains noise: punctuation, uppercase, common filler words
    ("the", "is", "a"), and different forms of the same word ("running",
    "runs", "ran"). ML models treat each unique string as a separate feature,
    so without cleaning, the model wastes resources on meaningless distinctions.

STEPS PERFORMED (in order):
    1. Lowercase          → "News" and "news" become the same token
    2. Remove punctuation → "fact!" and "fact" become the same token
    3. Remove stopwords   → Drop words like "the", "is", "at" (no signal)
    4. Stemming           → Reduce words to their root ("lying" → "lie")

Author: AI/ML Engineer
=============================================================================
"""

import re
import string
import logging

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ---------------------------------------------------------------------------
# Logging configuration
# All modules share the same logging setup for consistent output format.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Download required NLTK assets (safe to call multiple times)
# ---------------------------------------------------------------------------
def download_nltk_resources() -> None:
    """
    Download NLTK data files if they are not already present.

    NLTK needs external data (stopword lists, tokenizers) that don't ship
    with the base package. This function ensures they exist before use.
    """
    resources = ["stopwords", "punkt", "punkt_tab"]
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
            logger.debug(f"NLTK resource '{resource}' is ready.")
        except Exception as e:
            logger.warning(f"Could not download NLTK resource '{resource}': {e}")


# Download at import time so the rest of the module always works.
download_nltk_resources()


# ---------------------------------------------------------------------------
# Module-level singletons (created once, reused everywhere)
# ---------------------------------------------------------------------------
# PorterStemmer: rule-based algorithm that strips suffixes.
#   "running" → "run", "happily" → "happili", "studies" → "studi"
# It isn't linguistically perfect, but it's fast and effective for TF-IDF.
_stemmer = PorterStemmer()

# Stopwords: extremely common English words that carry almost zero meaning
# signal in fake-vs-real classification.
_stop_words = set(stopwords.words("english"))


# ---------------------------------------------------------------------------
# Core preprocessing function
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """
    Apply the full NLP preprocessing pipeline to a single string.

    Pipeline (order matters):
        lowercase → remove URLs → remove punctuation →
        tokenise → remove stopwords → stem → rejoin

    Args:
        text (str): Raw article text (title + body, or just body).

    Returns:
        str: Cleaned, stemmed string ready for TF-IDF vectorisation.

    Example:
        >>> clean_text("Breaking! Scientists are RUNNING experiments.")
        'break scientist run experi'
    """
    if not isinstance(text, str):
        # Guard against NaN / None values that sometimes appear in datasets.
        return ""

    # ── Step 1: Lowercase ────────────────────────────────────────────────
    # Ensures "Fake" and "fake" are treated as the same feature.
    text = text.lower()

    # ── Step 2: Remove URLs ──────────────────────────────────────────────
    # News text often contains links (http://...) that add noise.
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # ── Step 3: Remove HTML tags ─────────────────────────────────────────
    text = re.sub(r"<.*?>", "", text)

    # ── Step 4: Remove punctuation & special characters ──────────────────
    # string.punctuation = !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Also remove leftover non-alphabetic characters (digits, unicode junk)
    text = re.sub(r"[^a-z\s]", "", text)

    # ── Step 5: Tokenise (split into words) ──────────────────────────────
    tokens = text.split()

    # ── Step 6: Remove stopwords & stem ──────────────────────────────────
    # We combine these into a single loop for efficiency.
    cleaned_tokens = [
        _stemmer.stem(word)          # Stem: "running" → "run"
        for word in tokens
        if word not in _stop_words   # Skip: "the", "is", "at", …
        and len(word) > 2            # Skip single-letter noise ("a", "i")
    ]

    # ── Step 7: Rejoin into a string ─────────────────────────────────────
    # TF-IDF vectoriser expects a list of strings, not a list of token lists.
    return " ".join(cleaned_tokens)


# ---------------------------------------------------------------------------
# Dataset loading & merging
# ---------------------------------------------------------------------------
def load_and_merge_datasets(fake_path: str, true_path: str) -> pd.DataFrame:
    """
    Load Fake.csv and True.csv, attach labels, and merge into one DataFrame.

    LABELLING CONVENTION:
        Fake news → label = 0
        Real news → label = 1

    WHY BINARY LABELS?
        Scikit-learn classifiers expect numeric targets. 0/1 is the standard
        binary convention; it also makes probability interpretation intuitive
        (model.predict_proba gives P(real news)).

    Args:
        fake_path (str): Path to Fake.csv
        true_path (str): Path to True.csv

    Returns:
        pd.DataFrame: Merged dataframe with columns ['title', 'text',
                      'subject', 'date', 'label', 'content']

    Raises:
        FileNotFoundError: If either CSV file is missing.
        ValueError: If required columns are absent.
    """
    logger.info("Loading datasets …")

    # ── Load CSVs ─────────────────────────────────────────────────────────
    try:
        df_fake = pd.read_csv(fake_path)
        df_true = pd.read_csv(true_path)
    except FileNotFoundError as e:
        logger.error(f"Dataset file not found: {e}")
        raise

    logger.info(f"  Fake news articles loaded : {len(df_fake):,}")
    logger.info(f"  Real news articles loaded : {len(df_true):,}")

    # ── Validate columns ──────────────────────────────────────────────────
    required_cols = {"title", "text"}
    for name, df in [("Fake", df_fake), ("True", df_true)]:
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"{name}.csv is missing columns: {missing}")

    # ── Attach labels ─────────────────────────────────────────────────────
    df_fake["label"] = 0  # Fake  → 0
    df_true["label"] = 1  # Real  → 1

    # ── Merge & shuffle ───────────────────────────────────────────────────
    # random_state=42 → reproducible shuffle (same order every run)
    df = (
        pd.concat([df_fake, df_true], ignore_index=True)
        .sample(frac=1, random_state=42)   # Shuffle rows
        .reset_index(drop=True)
    )

    logger.info(f"  Total articles after merge: {len(df):,}")
    logger.info(f"  Label distribution:\n{df['label'].value_counts().to_string()}")

    # ── Create combined text column ───────────────────────────────────────
    # Combining title + text gives the model more signal than either alone.
    df["content"] = df["title"].fillna("") + " " + df["text"].fillna("")

    return df


# ---------------------------------------------------------------------------
# Apply preprocessing to a full dataframe
# ---------------------------------------------------------------------------
def preprocess_dataframe(df: pd.DataFrame, text_col: str = "content") -> pd.DataFrame:
    """
    Apply clean_text() to every row in `text_col`.

    This function adds a new column 'cleaned_text' so the original text is
    preserved for debugging and inspection.

    Args:
        df (pd.DataFrame): DataFrame containing the raw text column.
        text_col (str): Name of the column to clean. Default: 'content'.

    Returns:
        pd.DataFrame: Same DataFrame with an added 'cleaned_text' column.
    """
    logger.info(f"Preprocessing '{text_col}' column ({len(df):,} rows) …")

    df = df.copy()  # Never mutate the caller's dataframe
    df["cleaned_text"] = df[text_col].apply(clean_text)

    # Sanity check: warn if any rows became empty strings after cleaning
    empty_count = (df["cleaned_text"].str.strip() == "").sum()
    if empty_count:
        logger.warning(f"  {empty_count} rows became empty after preprocessing!")

    logger.info("  Preprocessing complete.")
    return df


# ---------------------------------------------------------------------------
# Standalone test / demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo_sentences = [
        "BREAKING: Scientists RUNNING experiments prove vaccines are DANGEROUS!!!",
        "The President signed a bill to reduce carbon emissions across the nation.",
        "Click HERE to find out the TRUTH they don't want you to know http://spam.com",
        "",   # Edge case: empty string
        None, # Edge case: None (NaN from CSV)
    ]

    print("\n=== Preprocessing Demo ===\n")
    for raw in demo_sentences:
        cleaned = clean_text(raw)
        print(f"  RAW     : {repr(raw)}")
        print(f"  CLEANED : {repr(cleaned)}")
        print()

"""
text_processor.py
─────────────────
All text-cleaning / normalisation logic lives here.
Keeping it separate from the prediction logic means:
  • Easy to unit-test
  • Easy to swap out (e.g. swap NLTK for spaCy later)
  • Routes stay thin and readable
"""

import re
import string
import unicodedata

import nltk
from nltk.corpus   import stopwords
from nltk.stem     import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Download required NLTK data on first import ─────────────────────────────
_NLTK_PACKAGES = ["punkt", "stopwords", "wordnet", "omw-1.4", "punkt_tab"]

def _ensure_nltk_data() -> None:
    for pkg in _NLTK_PACKAGES:
        try:
            # Check whether the data is already present
            nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
        except LookupError:
            logger.info("Downloading NLTK package: %s", pkg)
            nltk.download(pkg, quiet=True)

_ensure_nltk_data()

# ── Singletons (instantiated once, reused for every request) ─────────────────
_stemmer     = PorterStemmer()
_lemmatizer  = WordNetLemmatizer()
_stop_words  = set(stopwords.words("english"))


# ── Public API ───────────────────────────────────────────────────────────────

def clean_text(text: str, *, use_stemming: bool = False, use_lemmatization: bool = True) -> str:
    """
    Full preprocessing pipeline.

    Steps
    -----
    1. Unicode normalisation  → strip accents / non-ASCII
    2. Lower-case
    3. Remove URLs
    4. Remove HTML tags
    5. Remove punctuation & digits
    6. Tokenise
    7. Remove stop-words
    8. Stem  OR  Lemmatize  (controlled by kwargs)
    9. Re-join into a single string

    Parameters
    ----------
    text              : Raw input string from the API request.
    use_stemming      : Apply Porter stemming  (faster, less accurate).
    use_lemmatization : Apply WordNet lemmatization (slower, more accurate).
                        Ignored when use_stemming=True.

    Returns
    -------
    Cleaned, lower-cased, normalised string ready for TF-IDF vectorisation.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    # 1. Unicode → ASCII
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    # 2. Lower-case
    text = text.lower()

    # 3. Strip URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # 4. Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # 5. Remove punctuation and digits
    text = text.translate(str.maketrans("", "", string.punctuation + string.digits))

    # 6. Tokenise
    tokens = word_tokenize(text)

    # 7. Remove stop-words and very short tokens
    tokens = [t for t in tokens if t not in _stop_words and len(t) > 2]

    # 8. Stem or Lemmatize
    if use_stemming:
        tokens = [_stemmer.stem(t) for t in tokens]
    elif use_lemmatization:
        tokens = [_lemmatizer.lemmatize(t) for t in tokens]

    # 9. Re-join
    cleaned = " ".join(tokens)

    logger.debug("clean_text: %d chars → %d tokens → %d chars",
                 len(text), len(tokens), len(cleaned))

    return cleaned


def basic_clean(text: str) -> str:
    """
    Lightweight clean used for input validation display
    (does NOT affect the ML pipeline — use clean_text() for that).
    Strips extra whitespace and control characters only.
    """
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()

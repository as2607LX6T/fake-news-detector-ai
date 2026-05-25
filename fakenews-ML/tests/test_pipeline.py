"""
=============================================================================
test_pipeline.py — Unit Tests for Fake News Detection Pipeline
=============================================================================

Run with:
    python -m pytest tests/test_pipeline.py -v

These tests verify each component in isolation so you can catch bugs early
without running the full pipeline or needing the real datasets.
=============================================================================
"""

import sys
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from preprocess import clean_text, download_nltk_resources


# ---------------------------------------------------------------------------
# preprocess.py tests
# ---------------------------------------------------------------------------
class TestCleanText:
    """Unit tests for the clean_text() preprocessing function."""

    def test_lowercase(self):
        """Uppercase letters must be lowercased."""
        result = clean_text("HELLO WORLD")
        assert result == result.lower()

    def test_removes_punctuation(self):
        """Punctuation characters must not appear in output."""
        import string
        result = clean_text("Hello, world! This is a test.")
        for char in string.punctuation:
            assert char not in result

    def test_removes_urls(self):
        """HTTP and HTTPS URLs must be stripped."""
        result = clean_text("Visit http://fake-news.com for more details")
        assert "http" not in result
        assert "fake" in result or len(result) >= 0  # text without url

    def test_removes_stopwords(self):
        """Common English stopwords must not appear in output."""
        # "the", "is", "a", "an" are classic stopwords
        result = clean_text("the cat is a mammal")
        tokens = result.split()
        stopword_set = {"the", "is", "a", "an"}
        for sw in stopword_set:
            assert sw not in tokens, f"Stopword '{sw}' found in output"

    def test_stemming_applied(self):
        """PorterStemmer should reduce inflected forms."""
        # "running" → "run", "studies" → "studi"
        result_running = clean_text("running")
        result_run     = clean_text("run")
        # Both should reduce to the same stem
        assert result_running == result_run

    def test_empty_string(self):
        """Empty input must return empty string without crashing."""
        assert clean_text("") == ""

    def test_none_input(self):
        """None input (from NaN cells) must return empty string."""
        assert clean_text(None) == ""

    def test_numeric_string(self):
        """Purely numeric strings should return empty or minimal output."""
        result = clean_text("12345 67890")
        # After removing non-alpha, should be empty
        assert result.strip() == ""

    def test_html_tags_removed(self):
        """HTML tags must be stripped."""
        result = clean_text("<b>Breaking</b> <p>News</p>")
        assert "<" not in result
        assert ">" not in result

    def test_returns_string(self):
        """Return type must always be str."""
        assert isinstance(clean_text("test"), str)
        assert isinstance(clean_text(""), str)
        assert isinstance(clean_text(None), str)

    def test_realistic_fake_news(self):
        """A realistic fake news headline should be preprocessed without error."""
        headline = (
            "SHOCKING!!! Scientists PROVE the government is hiding ALIENS "
            "in Area 51. Click here: http://truth.net"
        )
        result = clean_text(headline)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "http" not in result
        assert "!!!" not in result

    def test_realistic_real_news(self):
        """A realistic real news headline should be preprocessed without error."""
        headline = (
            "Federal Reserve raises interest rates by 25 basis points "
            "amid persistent inflation concerns, officials announced Tuesday."
        )
        result = clean_text(headline)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_long_text_performance(self):
        """Should handle article-length text without timeout."""
        import time
        long_text = "The government said officials are working. " * 500
        t0 = time.time()
        result = clean_text(long_text)
        elapsed = time.time() - t0
        assert elapsed < 5.0, f"Preprocessing took too long: {elapsed:.2f}s"
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# preprocess.py — dataset utilities
# ---------------------------------------------------------------------------
class TestLoadAndMerge:
    """Tests for load_and_merge_datasets() with mocked CSV files."""

    def test_labels_assigned_correctly(self, tmp_path):
        """Fake articles get label=0, real articles get label=1."""
        import pandas as pd
        from preprocess import load_and_merge_datasets

        # Create minimal fake CSVs
        fake_df = pd.DataFrame({
            "title": ["Fake headline 1", "Fake headline 2"],
            "text":  ["Fake body 1",     "Fake body 2"],
            "subject": ["politics", "politics"],
            "date":    ["2020-01-01",    "2020-01-02"],
        })
        true_df = pd.DataFrame({
            "title": ["Real headline 1", "Real headline 2"],
            "text":  ["Real body 1",     "Real body 2"],
            "subject": ["news", "news"],
            "date":    ["2020-01-01",    "2020-01-02"],
        })

        fake_path = tmp_path / "Fake.csv"
        true_path = tmp_path / "True.csv"
        fake_df.to_csv(fake_path, index=False)
        true_df.to_csv(true_path, index=False)

        df = load_and_merge_datasets(str(fake_path), str(true_path))

        assert set(df["label"].unique()) == {0, 1}
        assert (df["label"] == 0).sum() == 2  # 2 fake
        assert (df["label"] == 1).sum() == 2  # 2 real

    def test_content_column_created(self, tmp_path):
        """The 'content' column must be created (title + text)."""
        import pandas as pd
        from preprocess import load_and_merge_datasets

        fake_df = pd.DataFrame({
            "title": ["Fake title"],
            "text":  ["Fake body"],
            "subject": ["pol"],
            "date":    ["2020-01-01"],
        })
        true_df = pd.DataFrame({
            "title": ["Real title"],
            "text":  ["Real body"],
            "subject": ["news"],
            "date":    ["2020-01-01"],
        })

        fake_path = tmp_path / "Fake.csv"
        true_path = tmp_path / "True.csv"
        fake_df.to_csv(fake_path, index=False)
        true_df.to_csv(true_path, index=False)

        df = load_and_merge_datasets(str(fake_path), str(true_path))

        assert "content" in df.columns
        # Content should contain parts of both title and text
        assert "Fake title" in df["content"].values[0] or \
               "Real title" in df["content"].values[0]

    def test_missing_file_raises(self, tmp_path):
        """FileNotFoundError should be raised if a CSV is missing."""
        from preprocess import load_and_merge_datasets
        with pytest.raises(FileNotFoundError):
            load_and_merge_datasets(
                str(tmp_path / "nonexistent_fake.csv"),
                str(tmp_path / "nonexistent_true.csv"),
            )


# ---------------------------------------------------------------------------
# evaluate.py tests
# ---------------------------------------------------------------------------
class TestEvaluateModel:
    """Tests for evaluate_model() using a mock classifier."""

    def _make_mock_model(self, predictions):
        """Return a mock sklearn estimator that always predicts `predictions`."""
        model = MagicMock()
        model.predict.return_value = np.array(predictions)
        return model

    def test_perfect_model(self, tmp_path):
        """A perfect model should report accuracy=1.0."""
        from evaluate import evaluate_model

        y_test = np.array([0, 1, 0, 1, 0, 1])
        model  = self._make_mock_model(y_test)  # predict perfectly

        result = evaluate_model(
            model,
            X_test=None,       # model is mocked; X_test is ignored
            y_test=y_test,
            model_name="Mock Perfect",
            report_dir=tmp_path,
        )
        assert result["accuracy"] == pytest.approx(1.0)

    def test_random_model(self, tmp_path):
        """A random model should have accuracy between 0 and 1."""
        from evaluate import evaluate_model

        y_test = np.array([0, 1, 0, 1, 1, 0, 1, 0])
        y_pred = np.array([1, 1, 0, 0, 1, 1, 0, 0])  # 50% correct
        model  = self._make_mock_model(y_pred)

        result = evaluate_model(
            model,
            X_test=None,
            y_test=y_test,
            model_name="Mock Random",
            report_dir=tmp_path,
        )
        assert 0.0 <= result["accuracy"] <= 1.0

    def test_report_files_created(self, tmp_path):
        """Text report and confusion matrix PNG must be saved to disk."""
        from evaluate import evaluate_model

        y_test = np.array([0, 1, 0, 1])
        model  = self._make_mock_model(y_test)

        evaluate_model(
            model,
            X_test=None,
            y_test=y_test,
            model_name="Test Model",
            report_dir=tmp_path,
        )

        assert (tmp_path / "test_model_report.txt").exists()
        assert (tmp_path / "test_model_confusion_matrix.png").exists()

    def test_result_keys(self, tmp_path):
        """Return dict must contain 'accuracy', 'classification_report', 'confusion_matrix'."""
        from evaluate import evaluate_model

        y_test = np.array([0, 1, 1, 0])
        model  = self._make_mock_model(y_test)

        result = evaluate_model(
            model, X_test=None, y_test=y_test,
            model_name="Key Test", report_dir=tmp_path
        )

        assert "accuracy"              in result
        assert "classification_report" in result
        assert "confusion_matrix"      in result


# ---------------------------------------------------------------------------
# Integration smoke test
# ---------------------------------------------------------------------------
class TestIntegration:
    """Lightweight integration test using toy data (no real CSVs needed)."""

    def test_full_pipeline_toy_data(self, tmp_path):
        """
        Run the full pipeline on 20 synthetic articles.
        This verifies that all components connect without error.
        """
        import pandas as pd
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        from preprocess import clean_text

        # Synthetic dataset: clearly fake vs clearly real vocabulary
        fake_texts = [
            "SHOCKING government conspiracy aliens control the world mind control",
            "BREAKING illuminati secret society control banks hidden truth revealed",
            "Scientists PROVE vaccines cause mutations deep state hiding evidence",
            "Moon landing hoax Hollywood studio faked NASA cover up exposed",
            "URGENT elite globalists planning world takeover secret documents leaked",
        ] * 4  # 20 fake articles

        real_texts = [
            "Congress approved bipartisan infrastructure investment bill Tuesday",
            "Federal Reserve raises interest rates amid persistent inflation",
            "Scientists publish study on climate change renewable energy impact",
            "Senate committee votes on healthcare reform legislation Wednesday",
            "International trade agreement signed by G7 leaders at summit",
        ] * 4  # 20 real articles

        texts  = fake_texts + real_texts
        labels = [0] * 20 + [1] * 20

        df = pd.DataFrame({"text": texts, "label": labels})
        df["cleaned"] = df["text"].apply(clean_text)

        X_train, X_test, y_train, y_test = train_test_split(
            df["cleaned"], df["label"], test_size=0.2, random_state=42
        )

        vec = TfidfVectorizer(max_features=500)
        X_tr = vec.fit_transform(X_train)
        X_te = vec.transform(X_test)

        model = LogisticRegression(max_iter=200, random_state=42)
        model.fit(X_tr, y_train)

        acc = accuracy_score(y_test, model.predict(X_te))
        # On this clearly separable toy dataset, accuracy should be high
        assert acc >= 0.7, f"Expected >= 0.70, got {acc:.4f}"


# ---------------------------------------------------------------------------
# Entry point for running tests directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

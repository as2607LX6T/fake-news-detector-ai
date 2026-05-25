"""
test_predict.py
───────────────
Automated tests for the /predict and /health endpoints.

Run with:
    pytest tests/ -v
"""

import pickle
import types
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
from fastapi.testclient import TestClient

# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def mock_model():
    """A minimal sklearn-like classifier that always predicts Fake (0)."""
    m = MagicMock()
    m.predict.return_value        = np.array([0])
    m.predict_proba.return_value  = np.array([[0.93, 0.07]])
    return m

@pytest.fixture(scope="session")
def mock_vectorizer():
    """A minimal sklearn-like vectorizer that returns a 1×1 sparse matrix."""
    from scipy.sparse import csr_matrix
    v = MagicMock()
    v.transform.return_value = csr_matrix(np.array([[0.5]]))
    return v

@pytest.fixture(scope="session")
def client(mock_model, mock_vectorizer):
    """TestClient with model/vectorizer mocked so no .pkl files are needed."""
    with patch("app.utils.model_loader._model",      mock_model), \
         patch("app.utils.model_loader._vectorizer", mock_vectorizer):
        from app.main import create_app
        app = create_app()
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


# ── Health tests ──────────────────────────────────────────────────────────────

def test_health_liveness(client):
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_health_readiness(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    data = r.json()
    assert "model" in data
    assert "vectorizer" in data


# ── Predict — happy path ──────────────────────────────────────────────────────

def test_predict_fake(client):
    payload = {"text": "SHOCKING: Scientists confirm vaccines contain microchips to track every citizen!"}
    r = client.post("/predict/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"]     == "success"
    assert data["prediction"] in ("Fake", "Real")
    assert "%" in data["confidence"]
    assert data["risk"]       in ("LOW", "MEDIUM", "HIGH")
    assert data["word_count"] > 0

def test_predict_returns_word_count(client):
    text = "This is a normal news article about science and technology."
    r    = client.post("/predict/", json={"text": text})
    assert r.status_code == 200
    assert r.json()["word_count"] == len(text.split())


# ── Predict — validation errors ───────────────────────────────────────────────

def test_predict_empty_text(client):
    r = client.post("/predict/", json={"text": ""})
    assert r.status_code in (400, 422)

def test_predict_too_short(client):
    r = client.post("/predict/", json={"text": "hi"})
    assert r.status_code in (400, 422)

def test_predict_missing_field(client):
    r = client.post("/predict/", json={})
    assert r.status_code == 422

def test_predict_wrong_type(client):
    r = client.post("/predict/", json={"text": 12345})
    # Pydantic will coerce int→str, so 200 is also acceptable here
    assert r.status_code in (200, 422)

def test_predict_too_long(client):
    r = client.post("/predict/", json={"text": "word " * 15_000})
    assert r.status_code in (400, 422)


# ── Root redirect ─────────────────────────────────────────────────────────────

def test_root_redirects_to_docs(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (301, 302, 307, 308)
    assert "/docs" in r.headers.get("location", "")

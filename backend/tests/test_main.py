"""
Tests for the FastAPI backend application.

These tests verify that the service starts correctly, exposes the expected
endpoints, and produces sensible predictions using a locally loaded dummy
model.  The dummy model is trained on random data with the same number
of features as the German Credit dataset.
"""

import os
import tempfile
import numpy as np
import joblib
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session", autouse=True)
def dummy_model(tmp_path_factory):
    """Create a dummy model and set environment variables for the app."""
    tmp_dir = tmp_path_factory.mktemp("models")
    model_path = tmp_dir / "dummy_model.pkl"

    # Generate a random binary classification problem with 20 features
    X = np.random.randn(100, 20)
    y = (np.random.rand(100) > 0.5).astype(int)
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression()
    model.fit(X, y)
    joblib.dump(model, model_path)

    # Set environment variables so the app loads this model
    os.environ["MODEL_LOCAL_PATH"] = str(model_path)
    os.environ.pop("MODEL_NAME", None)  # ensure remote loading is skipped
    yield model_path
    # Cleanup
    if os.path.exists(model_path):
        os.remove(model_path)


@pytest.fixture()
def client(dummy_model):
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_schema(client):
    response = client.get("/schema")
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    assert isinstance(data["features"], list)
    assert len(data["features"]) == 20


def test_predict(client):
    # Build a payload using the returned schema
    schema_resp = client.get("/schema")
    features_spec = schema_resp.json()["features"]
    payload = {spec["name"]: 0 for spec in features_spec}
    response = client.post("/predict", json={"features": payload})
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["probability"] <= 1.0
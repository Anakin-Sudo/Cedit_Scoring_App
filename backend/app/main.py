"""
FastAPI application exposing credit scoring endpoints.

The app loads an ML model on startup (either from a local pickle or the
Azure ML registry via MLflow).  It exposes a REST API used both by the
frontend and by external clients.  Prediction requests are logged to a
database for monitoring purposes.
"""

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .schemas import PredictionRequest, PredictionResponse
from .utils import get_model, get_feature_schema
from .crud import create_log_entry


# Create all tables on startup.  In production you may wish to manage
# migrations separately (e.g. using Alembic), but for a lightweight app this
# approach is sufficient.
app = FastAPI(title="Credit Scoring Service", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables and warm up the model cache."""
    Base.metadata.create_all(bind=engine)
    # Warm up model so first request is fast
    try:
        get_model()
    except Exception as exc:
        # Do not crash if model loading fails; raise on predict instead
        app.logger.warning(f"Model failed to load during startup: {exc}")


def get_db() -> Session:
    """Provide a database session to path operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    """Return basic health information."""
    return {"status": "ok"}


@app.get("/schema")
def schema() -> dict:
    """Return the expected input schema for predictions."""
    return get_feature_schema()


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, db: Session = Depends(get_db)) -> PredictionResponse:
    """
    Generate a prediction given applicant features.

    The input features are converted to a pandas DataFrame, passed through the
    loaded model, and the resulting class and probability are returned.  All
    requests are logged to the database.  A 500 error is raised if the model
    fails to load or prediction fails.
    """
    try:
        model, feature_list = get_model()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model is not available: {exc}")

    # Ensure all expected features are present
    missing = [f for f in feature_list if f not in request.features]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing features: {missing}")

    # Construct DataFrame in correct column order
    df = pd.DataFrame([{k: request.features.get(k) for k in feature_list}])

    # Make prediction
    try:
        proba = model.predict_proba(df)[:, 1][0]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    prediction = int(proba >= 0.5)

    # Persist log entry (fire‑and‑forget)
    try:
        create_log_entry(db, request.features, prediction, float(proba))
    except Exception as exc:
        # Log but don't break the response
        app.logger.warning(f"Failed to log prediction: {exc}")

    return PredictionResponse(prediction=prediction, probability=proba)
"""
Pydantic schemas used for request and response validation.

The `PredictionRequest` accepts a dictionary of feature names to values.  The
keys must match the feature names returned by the `/schema` endpoint.  The
values can be any JSON serialisable type; conversion to the appropriate
numeric or categorical type happens internally.  The `PredictionResponse`
returns the predicted class label and the probability of the positive class.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Incoming payload for the `/predict` endpoint."""

    features: Dict[str, Any] = Field(
        ..., description="Mapping of feature names to their raw input values"
    )


class PredictionResponse(BaseModel):
    """Outgoing payload from the `/predict` endpoint."""

    prediction: int = Field(..., description="Predicted class label")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of default")
"""
Utility functions for loading the ML model and exposing the input schema.

The service supports loading the model either from the MLflow registry in
Azure Machine Learning or from a local file for development and testing.
Model loading is cached on the first call.  To override the default
behaviour set `MODEL_LOCAL_PATH` in the environment.
"""

import os
from functools import lru_cache
from typing import Tuple, List, Dict, Any

import joblib
import mlflow
from mlflow import pyfunc
from pydantic import BaseModel


# List of feature names expected by the model.  These correspond to columns in
# the German Credit dataset minus the target column.  If you train a model on a
# different feature set be sure to update this list or derive it dynamically.
DEFAULT_FEATURES: List[str] = [
    "Status",
    "Duration",
    "CreditHistory",
    "Purpose",
    "CreditAmount",
    "Savings",
    "Employment",
    "InstallmentRate",
    "SexAndStatus",
    "OtherDetors",
    "ResidenceSince",
    "Property",
    "Age",
    "OtherInstallmentPlans",
    "Housing",
    "ExistingCredits",
    "Job",
    "PeopleLiable",
    "Telephone",
    "ForeignWorker",
]


@lru_cache(maxsize=1)
def get_model() -> Tuple[Any, List[str]]:
    """Load and cache the ML model.  Returns (model, feature_list)."""
    model_local_path = os.getenv("MODEL_LOCAL_PATH", "").strip()
    model_name = os.getenv("MODEL_NAME", "").strip()
    model_version = os.getenv("MODEL_VERSION", "").strip()

    # 1. Load from local path if specified
    if model_local_path:
        if not os.path.isfile(model_local_path):
            raise FileNotFoundError(
                f"MODEL_LOCAL_PATH set to '{model_local_path}' but the file does not exist"
            )
        model = joblib.load(model_local_path)
        return model, DEFAULT_FEATURES

    # 2. Load from MLflow registry in Azure ML
    if not model_name:
        raise EnvironmentError(
            "MODEL_NAME must be set to load the model from the registry or set MODEL_LOCAL_PATH"
        )

    # Construct model URI.  If version is empty, MLflow will resolve latest.
    version = model_version if model_version else None
    model_uri = f"models:/{model_name}/{version}" if version else f"models:/{model_name}"

    # Set registry URI if Azure ML workspace variables are present.  When running
    # inside Azure ML managed environments these environment variables are
    # automatically set.  For local development you must set them in `.env`.
    subscription_id = os.getenv("SUBSCRIPTION_ID")
    resource_group = os.getenv("RESOURCE_GROUP")
    workspace_name = os.getenv("WORKSPACE_NAME")
    if subscription_id and resource_group and workspace_name:
        mlflow.set_registry_uri(
            f"azureml://subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
        )

    try:
        model = pyfunc.load_model(model_uri)
    except Exception as exc:
        raise RuntimeError(f"Failed to load model from URI {model_uri}: {exc}")

    return model, DEFAULT_FEATURES


def get_feature_schema() -> Dict[str, List[Dict[str, str]]]:
    """Return a serialisable representation of the feature schema.

    The frontend uses this endpoint to dynamically render form fields.
    You can extend the returned dictionaries with additional metadata such
    as categorical value choices.
    """
    schema = []
    for feature in DEFAULT_FEATURES:
        schema.append({"name": feature, "type": "string"})
    return {"features": schema}
#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Download the latest or specified version of a registered MLflow model from
# Azure Machine Learning.  The model name and version are read from your
# `.env` file.  The downloaded model artefact will be placed in
# `backend/model/` and can then be copied into your Docker image during
# build.
#
# Prerequisites:
#   - You must have run `bash_scripts/az_login.sh` or otherwise logged in
#     (the script uses DefaultAzureCredential behind the scenes).
#   - `mlflow` must be installed in your Python environment (see backend
#     requirements.txt).
#
# Usage:
#   bash bash_scripts/download_model.sh
# -----------------------------------------------------------------------------

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$SCRIPT_DIR/.."

# Load environment variables
set -a
if [ -f "$REPO_ROOT/.env" ]; then
  source "$REPO_ROOT/.env"
else
  echo "⚠️  .env file not found at repository root. Copy .env.example and fill it in."
  exit 1
fi
set +a

MODEL_DIR="$REPO_ROOT/backend/model"
mkdir -p "$MODEL_DIR"

echo "Downloading ML model '$MODEL_NAME' (version: ${MODEL_VERSION:-latest})..."

# Run the Python helper script
python "$REPO_ROOT/backend/scripts/download_model.py" \
  --model-name "$MODEL_NAME" \
  --model-version "$MODEL_VERSION" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$WORKSPACE_NAME" \
  --output-dir "$MODEL_DIR"

echo "Model downloaded to $MODEL_DIR"
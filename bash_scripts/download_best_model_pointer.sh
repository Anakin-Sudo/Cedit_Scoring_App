#!/usr/bin/env bash
set -e

REPO_ROOT="credit_scoring_app"

# Get latest completed job
JOB_ID=$(az ml job list \
  --resource-group $AZURE_RESOURCE_GROUP \
  --workspace-name $AZURE_WORKSPACE_NAME \
  --query "[?display_name=='${TRAINING_PIPELINE_NAME}' && status=='Completed'] | max_by(@,&created_time).name" \
  -o tsv)

echo "ℹ️ Latest completed training job: $JOB_ID"

# Download pointer file
DEST_DIR="$REPO_ROOT/backend/model"
mkdir -p "$DEST_DIR"

az ml job download \
  --name "$JOB_ID" \
  --resource-group $AZURE_RESOURCE_GROUP \
  --workspace-name $AZURE_WORKSPACE_NAME \
  --outputs best_model_pointer_file \
  --download-path "$DEST_DIR"

mv "$DEST_DIR/best_model_pointer_file" "$DEST_DIR/best_model.txt"

# Download artifact using MLflow
MODEL_URI=$(cat "$DEST_DIR/best_model.txt")
python -m pip install mlflow azureml-mlflow
mlflow artifacts download -u "$MODEL_URI" -d "$DEST_DIR"

echo "✅ Model artifact downloaded to $DEST_DIR"

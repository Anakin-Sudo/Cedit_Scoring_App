#!/usr/bin/env bash
set -e

ACR_NAME=$1
RESOURCE_GROUP=$2
BACKEND_CONTAINER_NAME=$3
ACI_LOCATION=$4

BACKEND_DIR="credit_scoring_app/backend"

# Build backend image (with pre-downloaded model)
docker build -t "$ACR_NAME.azurecr.io/credit-scoring-backend:latest" "$BACKEND_DIR"

# Push to ACR
az acr login --name "$ACR_NAME"
docker push "$ACR_NAME.azurecr.io/credit-scoring-backend:latest"

# Clean old container
az container delete --name "$BACKEND_CONTAINER_NAME" --resource-group "$RESOURCE_GROUP" --yes || true

# Deploy new backend container
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$BACKEND_CONTAINER_NAME" \
  --image "$ACR_NAME.azurecr.io/credit-scoring-backend:latest" \
  --cpu 1 --memory 2 \
  --registry-login-server "$ACR_NAME.azurecr.io" \
  --restart-policy Always

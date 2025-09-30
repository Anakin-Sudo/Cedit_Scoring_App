#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Build, push and deploy the FastAPI backend to Azure Container Instances.
#
# This script expects the Azure CLI to be installed and you to be logged in via
# `az login` (see `az_login.sh`).  It reads configuration from `.env` and
# publishes the backend image to your Azure Container Registry (ACR) before
# creating or updating a container instance in your specified resource group.
#
# Note: This script is provided for local convenience.  GitHub Actions uses
# similar commands in `.github/workflows/deploy.yml` for automated CI/CD.
# -----------------------------------------------------------------------------

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$SCRIPT_DIR/.."

set -a
if [ -f "$REPO_ROOT/.env" ]; then
  source "$REPO_ROOT/.env"
else
  echo "⚠️  .env file not found at repository root. Copy .env.example and fill it in."
  exit 1
fi
set +a

# Validate required variables
if [ -z "$ACR_NAME" ] || [ -z "$RESOURCE_GROUP" ] || [ -z "$BACKEND_IMAGE_NAME" ]; then
  echo "❌ ACR_NAME, RESOURCE_GROUP and BACKEND_IMAGE_NAME must be set in .env"
  exit 1
fi

FULL_IMAGE_NAME="${ACR_NAME}.azurecr.io/${BACKEND_IMAGE_NAME}:latest"

echo "Logging into Azure Container Registry: $ACR_NAME"
az acr login --name "$ACR_NAME"

echo "Building backend Docker image: $FULL_IMAGE_NAME"
docker build -t "$FULL_IMAGE_NAME" -f "$REPO_ROOT/backend/Dockerfile" "$REPO_ROOT"

echo "Pushing image to ACR"
docker push "$FULL_IMAGE_NAME"

# Prepare environment variables string for ACI
ENV_ARGS=""
while IFS='=' read -r key value; do
  # Skip comments and empty lines
  if [[ "$key" =~ ^# ]] || [ -z "$key" ]; then
    continue
  fi
  ENV_ARGS+=" $key=$value"
done < <(grep -v '^#' "$REPO_ROOT/.env" | grep '=')

echo "Creating or updating Azure Container Instance: $BACKEND_CONTAINER_NAME"
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$BACKEND_CONTAINER_NAME" \
  --image "$FULL_IMAGE_NAME" \
  --ports 8000 \
  --environment-variables $ENV_ARGS \
  --restart-policy Always \
  --cpu 1 --memory 2

echo "Deployment complete.  Use 'az container show --resource-group $RESOURCE_GROUP --name $BACKEND_CONTAINER_NAME --query ipAddress.fqdn' to obtain the URL."
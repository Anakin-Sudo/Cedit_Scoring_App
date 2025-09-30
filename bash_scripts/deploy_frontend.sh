#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Build, push and deploy the React frontend to Azure Container Instances.
#
# Like the backend script, this helper reads configuration from `.env` and
# publishes the compiled frontend static site to ACR.  The resulting Nginx
# container serves the React build on port 80.  Before running, ensure you
# have authenticated with Azure CLI (see `az_login.sh`) and that your ACR
# exists.  For automated deployment see `.github/workflows/deploy.yml`.
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
if [ -z "$ACR_NAME" ] || [ -z "$RESOURCE_GROUP" ] || [ -z "$FRONTEND_IMAGE_NAME" ]; then
  echo "❌ ACR_NAME, RESOURCE_GROUP and FRONTEND_IMAGE_NAME must be set in .env"
  exit 1
fi

FULL_IMAGE_NAME="${ACR_NAME}.azurecr.io/${FRONTEND_IMAGE_NAME}:latest"

echo "Logging into Azure Container Registry: $ACR_NAME"
az acr login --name "$ACR_NAME"

echo "Building frontend Docker image: $FULL_IMAGE_NAME"
docker build -t "$FULL_IMAGE_NAME" -f "$REPO_ROOT/frontend/Dockerfile" "$REPO_ROOT/frontend"

echo "Pushing image to ACR"
docker push "$FULL_IMAGE_NAME"

echo "Creating or updating Azure Container Instance: $FRONTEND_CONTAINER_NAME"
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FRONTEND_CONTAINER_NAME" \
  --image "$FULL_IMAGE_NAME" \
  --ports 80 \
  --restart-policy Always \
  --cpu 1 --memory 1

echo "Deployment complete.  Use 'az container show --resource-group $RESOURCE_GROUP --name $FRONTEND_CONTAINER_NAME --query ipAddress.fqdn' to obtain the URL."
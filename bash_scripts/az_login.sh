#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Authenticate with Azure using the tenant specified in your `.env` file.
#
# This script sources environment variables from the repository root and
# performs `az login` against the configured tenant.  It relies on your
# machine being configured with Azure CLI.  In non‑interactive environments
# (e.g. GitHub Actions) authentication is handled by the azure/login action
# instead of this script.
# -----------------------------------------------------------------------------

set -e

# Resolve the location of this script and the repository root
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

echo "Logging in to Azure tenant $TENANT_ID..."
az login --tenant "$TENANT_ID"
echo "Logged in successfully."
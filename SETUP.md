# Setup Instructions - Serving Repo

This document details the configuration and deployment steps required for the serving layer
of the Credit Scoring Application.

---

## GitHub Secrets

The following secrets **must** be set in GitHub → Settings → Secrets and variables → Actions:

- `AZURE_CLIENT_ID`  
- `AZURE_CLIENT_SECRET`  
- `AZURE_TENANT_ID`  
- `AZURE_SUBSCRIPTION_ID`  
- `AZURE_RESOURCE_GROUP`  
- `AZURE_WORKSPACE_NAME`  
- `ACR_NAME`  
- `BACKEND_CONTAINER_NAME`  
- `FRONTEND_CONTAINER_NAME`  
- `ACI_LOCATION`  
- `TRAINING_PIPELINE_NAME`  

Optional runtime overrides (only if you want to customize):  
- `DB_PATH` (default: `app.db`)  
- `REACT_APP_API_URL` (default: `http://localhost:8000`)  

---

## RBAC Requirements

The service principal used for CI/CD must have the following role assignments:

| Resource | Role | Purpose |
|----------|------|---------|
| Resource Group (`group-1`) | Contributor | Deploy ACI, manage AML jobs |
| Container Registry (`creditscoringregistry`) | AcrPush | Push/pull Docker images |
| AML Workspace | Inherited via Contributor on RG | Access jobs & outputs |

---

## Deployment Scripts

- **`download_best_model_pointer.sh`**:  
  Downloads the latest `best_model_pointer_file` from AML, extracts the model URI, and downloads the artifact into `backend/model/`.

- **`deploy_backend.sh` / `deploy_frontend.sh`**:  
  Scripts to build and push Docker images to ACR and deploy them as ACI containers.  
  They accept arguments passed from GitHub Actions:  

  ```bash
  ACR_NAME=$1
  RESOURCE_GROUP=$2
  BACKEND_CONTAINER_NAME=$3
  ACI_LOCATION=$4
  ```

---

## Monitoring and Drift

- Predictions are stored in SQLite (`app.db`).  
- Training baseline statistics must be exported to `backend/model/training_baseline.csv` during training.  
- The script `backend/scripts/check_drift.py` compares production vs. baseline (PSI/KL metrics).  
- Scheduled workflow `monitor.yml` executes drift detection weekly.

---

## Local Environment

For development only, `.env.example` provides template values.  
**Do not use `.env` in CI/CD** — GitHub Actions secrets are the authoritative source.  

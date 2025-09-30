# Credit Scoring Application - Serving Repo

This repository contains the **serving layer** for the Credit Scoring project.  
It integrates with the **Azure ML training pipeline** by fetching the best model (via pointer file),
embedding it into a Dockerized **FastAPI backend**, and serving predictions through a **React frontend**.

---

## Components

- **Backend (FastAPI)**:  
  - Serves the credit scoring model via REST API.  
  - Logs predictions and metadata into a lightweight SQLite database (`app.db`).  
  - Model artifact is baked into the container at build time.  

- **Frontend (React)**:  
  - Provides a web interface for users to submit requests.  
  - Calls the backend API for predictions.  

- **Deployment (Azure)**:  
  - Docker images are built and pushed to **Azure Container Registry (ACR)**.  
  - Images are deployed as **Azure Container Instances (ACI)**: one for backend, one for frontend.  

- **Monitoring**:  
  - Predictions logged in SQLite enable model drift checks.  
  - A scheduled GitHub Action runs drift analysis (`check_drift.py`).  

---

## CI/CD Workflows

The repository includes GitHub Actions workflows:

- **CI (`ci.yml`)**:  
  Installs dependencies, runs tests, and validates builds.

- **CD (`deploy.yml`)**:  
  - Logs into Azure using a service principal.  
  - Downloads the **best model pointer file** and resolves it into a model artifact.  
  - Builds backend and frontend Docker images.  
  - Pushes them to ACR.  
  - Deploys containers to ACI.

- **Monitoring (`monitor.yml`)**:  
  Runs drift detection weekly against the logged SQLite predictions.

---

## Setup

Full setup instructions, including required secrets, environment configuration, and role assignments, are provided in [SETUP.md](SETUP.md).

---

## Local Development

For developers who wish to run locally:

```bash
# Backend
cd credit_scoring_app/backend
uvicorn app.main:app --reload

# Frontend
cd credit_scoring_app/frontend
npm install
npm start
```

Use `.env.example` as a template for local environment variables.  
For deployment, all secrets are managed in GitHub Actions. See `SETUP.md`.

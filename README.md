# Credit Scoring Web Application

This repository implements a lightweight web application that wraps the credit
scoring machine learning pipeline you provided.  The goal of the app is to
expose a simple REST API for scoring loan applicants, present a user‑friendly
React interface for entering applicant information, log all requests for
monitoring, and provide a complete CI/CD pipeline using GitHub Actions and
Azure Container Instances (ACI).  All configuration values are sourced from
a `.env` file, consistent with your existing pipeline.

## Repository structure

```
credit_scoring_app/
│
├── .env.example            # Template for environment variables (copy to `.env`)
├── .gitignore              # Ignore compiled artifacts, secrets and caches
├── bash_scripts/           # Bash helpers for Azure login, model download & deployment
├── backend/                # FastAPI backend service and its tests
│   ├── app/
│   │   ├── main.py         # Entry point defining API endpoints
│   │   ├── database.py     # SQLAlchemy database configuration
│   │   ├── models.py       # ORM model for logging requests
│   │   ├── schemas.py      # Pydantic models defining API contracts
│   │   ├── crud.py         # CRUD helpers for saving logs
│   │   └── utils.py        # Functions for loading the ML model and inferring schemas
│   ├── requirements.txt    # Python dependencies for backend
│   ├── Dockerfile          # Build instructions for backend container
│   └── tests/              # Unit tests for API and utilities
├── frontend/               # React frontend code, tests and Dockerfile
│   ├── public/
│   │   └── index.html      # Entry HTML file injected by React
│   ├── src/
│   │   ├── index.jsx       # Frontend entry point
│   │   ├── App.jsx         # Top‑level React component
│   │   ├── api.js          # Helper for calling the backend API
│   │   └── components/     # Form and result display components
│   ├── package.json        # Node dependencies and scripts
│   ├── Dockerfile          # Build instructions for frontend container
│   └── tests/              # Jest/RTL tests for React components
├── .github/
│   └── workflows/
│       ├── ci.yml          # Continuous integration – linting and tests
│       └── deploy.yml      # Continuous deployment – build & deploy to ACI
└── README.md               # This file
```

## Backend overview

The backend is a FastAPI application that exposes three main endpoints:

| Endpoint            | Method | Description                                               |
|-------------------- |------- |-----------------------------------------------------------|
| `/health`           | `GET`  | Liveness endpoint returning service status               |
| `/schema`           | `GET`  | Returns the list of features expected by the model       |
| `/predict`          | `POST` | Accepts applicant data and returns the predicted outcome |

When the application starts it loads a scikit‑learn pipeline from the MLflow
registry in your Azure ML workspace.  The model name and version are read
from environment variables.  For development and testing you can bypass
Azure entirely by providing `MODEL_LOCAL_PATH` in your `.env`; in this case
the backend will load the model from disk instead.

All prediction requests, including the input payload, predicted class and
probability, are logged to a lightweight SQLite database using SQLAlchemy.
This database file lives inside the container by default but can be mounted to
external storage for persistent logging.  The logging logic is isolated in
`crud.py` and can easily be extended to push logs to Application Insights or
Azure Monitor.  For production use we recommend configuring the Azure
Monitoring agent on your ACI deployment and enabling diagnostic settings to
stream container logs to your Log Analytics workspace.  Details on how to
configure Azure Monitor are outside the scope of this sample but pointers
are provided in `SETUP.md`.

## Frontend overview

The frontend is a React application that fetches the input feature schema
from `/schema`, dynamically renders a form for the user to fill in, submits
the form to `/predict`, and displays the model’s response.  A basic
responsive layout is used, but you are free to customise styling.  The
frontend uses Axios for HTTP calls and reads the backend base URL from
`REACT_APP_API_URL` at build time.  A Dockerfile is provided to build the
static React bundle and serve it with Nginx.

## CI/CD

Two GitHub Actions workflows are provided:

1. **CI** (`.github/workflows/ci.yml`) – triggered on every push and pull
   request to `main`.  It performs a fast feedback loop by installing Python
   and Node dependencies, running backend unit tests with pytest, running
   frontend unit tests with Jest, and performing a lightweight lint.

2. **Deployment** (`.github/workflows/deploy.yml`) – triggered manually via
   the workflow dispatch or on push to a release branch.  It logs into
   Azure using a service principal (stored in repo secrets), builds the
   backend and frontend Docker images, pushes them to your Azure Container
   Registry, and deploys them to Azure Container Instances.  The workflow
   reads all configuration from your `.env` file, which you must upload as
   an encrypted repository secret (`ENV_FILE`).  The deployment script uses
   `az container create` to start new containers or update existing ones.

## Getting started

1. **Clone the repository** and copy `.env.example` to `.env`.  Fill in the
   required values: Azure subscription, tenant, resource group, workspace,
   ACR name, container names, and model details.  Do not commit the `.env`
   file.

2. **Install backend dependencies**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Run locally**:  In two terminals run the backend and frontend:
   ```bash
   # Terminal 1 (backend)
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2 (frontend)
   cd frontend
   npm start
   ```
   The frontend will automatically proxy API requests to
   `REACT_APP_API_URL`, which defaults to `http://localhost:8000`.

5. **Run tests**:  At the repo root you can run all tests via the provided
   scripts:
   ```bash
   # Backend tests
   cd backend
   pytest -q

   # Frontend tests
   cd ../frontend
   npm test
   ```

6. **Download the model** (optional):  If you want to include the latest
   model artefact when building the backend image you can run the provided
   script after logging in to Azure:
   ```bash
   bash bash_scripts/az_login.sh           # authenticate using your tenant
   bash bash_scripts/download_model.sh     # downloads the MLflow model
   ```
   This script uses `mlflow` under the hood to fetch the registered model
   specified in your `.env` and saves it to `backend/model`.  The backend
   Dockerfile copies this folder into the container image.

7. **Deploy**:  Push your changes to GitHub and trigger the deployment
   workflow.  The workflow reads your `.env` file from a secret and will
   build, push and deploy both services.  Alternatively you can run the
   scripts in `bash_scripts` manually if you prefer deploying from your
   machine using the Azure CLI.

## Additional configuration and monitoring

This sample emphasises convention over configuration.  Almost all values
needed to run and deploy the app live in `.env`.  Should you need to
customise behaviour beyond what environment variables allow (for example,
adjusting the Kestrel worker count for Uvicorn or changing the React build
output), consult the associated `Dockerfile`s and update them accordingly.

For production monitoring we recommend enabling diagnostic logging on your
ACI containers and forwarding logs to a Log Analytics workspace.  You can
also configure Application Insights by installing the `opencensus-ext-azure`
package and adding a trace exporter in `backend/app/utils.py`.  See
[Setup guide](SETUP.md) for pointers on enabling these features.

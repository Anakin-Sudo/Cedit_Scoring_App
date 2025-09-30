# Additional Setup Guidance

This document complements the primary `README.md` by covering tasks that fall
outside of pure configuration.  It provides guidance on provisioning Azure
resources, enabling monitoring, and preparing your environment for CI/CD.

## 1. Provision Azure resources

Before deploying the web application you must provision several Azure
resources.  Many of these can be created via the portal or the Azure CLI.

1. **Azure Machine Learning workspace**:  The ML pipeline you supplied runs
   in an AML workspace.  Create a workspace in the desired region (e.g.
   `eastus`) and note the subscription id, resource group and workspace name.
2. **Azure Container Registry (ACR)**:  Create an ACR in the same region as
   your workspace to store Docker images.  Use the CLI command:
   ```bash
   az acr create --resource-group <resource-group> --name <acr-name> --sku Basic --location <region>
   ```
   The `<acr-name>` should match the `ACR_NAME` value in `.env`.
3. **Service Principal for GitHub Actions**:  Create a service principal with
   `Contributor` role scoped to your resource group.  Store the client id,
   tenant id and subscription id in GitHub repository secrets.  Refer to
   `bash_scripts/create_service_principal.sh` in the original pipeline for an
   example.
4. **Key Vault & Storage (optional)**:  If you wish to manage secrets or
   persist logs centrally, create an Azure Key Vault and storage account.  The
   provided application does not rely on these services directly but you can
   extend it by reading secrets from Key Vault and mounting a file share for
   SQLite.

## 2. Configure monitoring

Logging prediction requests to the SQLite database is only part of a robust
monitoring strategy.  To integrate with Azure Monitor:

1. Enable diagnostic settings on your container group to send stdout/stderr
   logs to a Log Analytics workspace:
   ```bash
   az monitor diagnostic-settings create \
     --resource $(az container show --resource-group $RESOURCE_GROUP --name $BACKEND_CONTAINER_NAME --query id -o tsv) \
     --workspace <log-analytics-workspace-id> \
     --logs '[{"category":"ContainerInstanceLogs","enabled":true}]'
   ```
2. Consider instrumenting the FastAPI application with OpenTelemetry.  The
   [`opencensus-ext-azure`](https://pypi.org/project/opencensus-ext-azure/)
   package can export traces and metrics to Application Insights.  You can
   initialise a tracer in `backend/app/utils.py` and wrap API calls to emit
   spans for each prediction.
3. For data drift or model performance monitoring, log prediction inputs and
   outputs along with timestamps to a central database (e.g. Azure SQL or
   Cosmos DB).  The current implementation writes to SQLite only; you can
   replace the `DATABASE_URL` in `database.py` with a connection string to
   your database of choice.

## 3. Running the ML pipeline and refreshing the model

Your original repository contains a GitHub Actions workflow (`azure-ml-pipeline.yml`) that
triggers the training pipeline.  After the pipeline completes it writes a
pointer file containing the MLflow URI of the champion model.  You may wish to
automate updating the web application when a new model is registered.  There
are two strategies:

1. **Manual refresh**:  After a successful pipeline run, update `MODEL_VERSION`
   in your `.env` and re‑deploy.  The deployment workflow will download the
   specified version.
2. **Automated refresh**:  Create a GitHub Actions workflow that listens for
   MLflow registry events (such as a new model version) or poll on a schedule.
   When a new version appears, trigger the `deploy.yml` workflow with the
   appropriate version number.  Use the Azure ML Python SDK to query the
   registry (see `backend/scripts/download_model.py` for an example).

## 4. Local development tips

* Use the provided `dummy_model` fixture in the backend tests as a starting
  point for local development.  You can point `MODEL_LOCAL_PATH` at any
  pickled scikit‑learn pipeline to avoid interacting with Azure when
  iterating on the API.
* Leverage `docker-compose` (not included) to spin up the backend and
  frontend locally.  A simple compose file would mount the local `.env` and
  database volume and define two services exposing ports 8000 and 3000.
* Run `npm run dev` in the `frontend` directory to enable hot reloading while
  editing React components.  The development server proxies API requests to
  `localhost:8000` by default.

## 5. Security considerations

Always treat the `.env` file as sensitive.  Never commit it to version
control.  Use GitHub Secrets for CI/CD and consider storing secrets in
Azure Key Vault for runtime access.  Configure CORS policies in FastAPI
(see `fastapi.middleware.cors`) if you expose the backend to untrusted
origins.

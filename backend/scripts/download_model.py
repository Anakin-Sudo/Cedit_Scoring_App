"""
Helper script for downloading a registered ML model from Azure Machine Learning.

Usage
-----
Run this script via `bash_scripts/download_model.sh` which populates most
arguments from your `.env`.  You can also invoke it directly:

```
python download_model.py \
    --model-name credit_model_xgb \
    --model-version 1 \
    --subscription-id <sub_id> \
    --resource-group <rg> \
    --workspace-name <ws> \
    --output-dir backend/model
```

If the model version is omitted the script will fetch the latest version
registered in the workspace.

Requirements
------------
This script depends on `azure-ai-ml` and `mlflow`.  See
`backend/requirements.txt` for details.  You must also be authenticated to
Azure (e.g. via `az login`) for `DefaultAzureCredential` to resolve your
credentials.
"""

import argparse
import os
from pathlib import Path
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download model from Azure ML")
    parser.add_argument("--model-name", required=True, help="Name of the registered model")
    parser.add_argument("--model-version", default="", help="Version of the model; latest if omitted")
    parser.add_argument("--subscription-id", required=True, help="Azure subscription id")
    parser.add_argument("--resource-group", required=True, help="Azure resource group name")
    parser.add_argument("--workspace-name", required=True, help="Azure ML workspace name")
    parser.add_argument("--output-dir", required=True, help="Destination directory for downloaded model")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    ml_client = MLClient(
        credential=cred,
        subscription_id=args.subscription_id,
        resource_group_name=args.resource_group,
        workspace_name=args.workspace_name,
    )

    # Determine model version
    version = args.model_version.strip()
    if not version:
        # `get` without version returns the latest by default
        latest_model = ml_client.models.get(name=args.model_name)
        version = latest_model.version
        print(f"Latest version for model '{args.model_name}' is {version}.")

    # Ensure output directory exists
    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(
        f"Downloading model '{args.model_name}' version '{version}' to '{out_path}'."
    )
    ml_client.models.download(
        name=args.model_name,
        version=version,
        download_path=str(out_path),
    )
    print("Download completed.")


if __name__ == "__main__":
    main()
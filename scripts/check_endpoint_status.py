"""Script to check endpoint deployment status."""

import typer
from google.cloud import aiplatform

from src.constants import PROJECT_ID, REGION


def check_endpoint_status(endpoint_id: str):
    """Check the status of an endpoint deployment."""
    aiplatform.init(project=PROJECT_ID, location=REGION)

    endpoint = aiplatform.Endpoint(
        f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{endpoint_id}"
    )

    print(f"Endpoint: {endpoint.display_name}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"Resource Name: {endpoint.resource_name}")
    print()

    deployed_models = endpoint.gca_resource.deployed_models
    
    if not deployed_models:
        print("⏳ No models deployed yet. Deployment in progress...")
    else:
        print(f"✅ {len(deployed_models)} model(s) deployed:")
        for model in deployed_models:
            print(f"  - Model: {model.display_name}")
            print(f"    ID: {model.id}")
            print(f"    Machine Type: {model.dedicated_resources.machine_spec.machine_type}")
            print(f"    Min Replicas: {model.dedicated_resources.min_replica_count}")
            print(f"    Max Replicas: {model.dedicated_resources.max_replica_count}")
            if model.dedicated_resources.machine_spec.accelerator_type:
                print(f"    Accelerator: {model.dedicated_resources.machine_spec.accelerator_type}")
                print(f"    Accelerator Count: {model.dedicated_resources.machine_spec.accelerator_count}")


if __name__ == "__main__":
    typer.run(check_endpoint_status)

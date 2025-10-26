"""Script to deploy a model to a Vertex AI endpoint."""

import typer
from google.cloud import aiplatform

from src.constants import PROJECT_ID, REGION


def deploy_model(
    model_name: str,
    endpoint_display_name: str = "enzo-synesthetic-dj-endpoint",
    machine_type: str = "n1-standard-4",
    accelerator_type: str = "NVIDIA_TESLA_T4",
    accelerator_count: int = 1,
):
    """Deploy a model to a Vertex AI endpoint."""
    aiplatform.init(project=PROJECT_ID, location=REGION)

    # Get the model
    model = aiplatform.Model(model_name)
    print(f"Model retrieved: {model.display_name}")

    # Create or get endpoint
    endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{endpoint_display_name}"'
    )
    
    if endpoints:
        endpoint = endpoints[0]
        print(f"Using existing endpoint: {endpoint.display_name}")
    else:
        endpoint = aiplatform.Endpoint.create(display_name=endpoint_display_name)
        print(f"Created new endpoint: {endpoint.display_name}")

    # Deploy model to endpoint
    print("Deploying model to endpoint...")
    model.deploy(
        endpoint=endpoint,
        deployed_model_display_name=model.display_name,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        min_replica_count=1,
        max_replica_count=1,
    )

    print(f"Model deployed successfully!")
    print(f"Endpoint ID: {endpoint.name.split('/')[-1]}")
    print(f"Endpoint resource name: {endpoint.resource_name}")


if __name__ == "__main__":
    typer.run(deploy_model)

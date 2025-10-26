"""Main constants of the project."""

import os
from pathlib import Path

# Paths
PROJECT_ROOT_PATH = Path(__file__).parents[1]

# GCP Configuration
PROJECT_ID: str | None = os.getenv("GCP_PROJECT_ID")
REGION: str = os.getenv("GCP_REGION", "europe-west9")
BUCKET_NAME: str | None = os.getenv("GCP_BUCKET_NAME")
ENDPOINT_ID: str | None = os.getenv("GCP_ENDPOINT_ID")
PROJECT_NUMBER: str | None = os.getenv("GCP_PROJECT_NUMBER")

# Paths
PIPELINE_ROOT_PATH: str = f"{BUCKET_NAME}/vertexai-pipeline-root/"

# Synesthetic DJ dataset configuration
DEFAULT_DATA_PREFIX = "synesthetic_dj"
_default_samples = (
    f"gs://{BUCKET_NAME}/{DEFAULT_DATA_PREFIX}/mood_samples.csv"
    if BUCKET_NAME
    else None
)
_default_catalog = (
    f"gs://{BUCKET_NAME}/{DEFAULT_DATA_PREFIX}/mood_catalog.csv"
    if BUCKET_NAME
    else None
)
MOOD_SAMPLES_URI: str | None = os.getenv("MOOD_SAMPLES_URI", _default_samples)
MOOD_CATALOG_URI: str | None = os.getenv("MOOD_CATALOG_URI", _default_catalog)

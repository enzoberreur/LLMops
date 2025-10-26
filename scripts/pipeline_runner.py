"""Pipeline compilation and submission utilities for Vertex AI."""

from google.cloud import aiplatform
from kfp import compiler

from src.constants import (
    MOOD_CATALOG_URI,
    MOOD_SAMPLES_URI,
    PIPELINE_ROOT_PATH,
    PROJECT_ID,
    REGION,
)
from src.pipelines.model_training_pipeline import model_training_pipeline

if __name__ == "__main__":
    aiplatform.init(project=PROJECT_ID, location=REGION)

    if not MOOD_SAMPLES_URI or not MOOD_CATALOG_URI:
        raise ValueError(
            "MOOD_SAMPLES_URI and MOOD_CATALOG_URI must be configured before running the pipeline."
        )

    pipeline_name = "model_training_pipeline"
    compiler.Compiler().compile(
        pipeline_func=model_training_pipeline,  # type: ignore
        package_path=f"{pipeline_name}.json",
    )
    job = aiplatform.PipelineJob(
        display_name=pipeline_name,
        template_path=f"{pipeline_name}.json",
        pipeline_root=f"gs://{PIPELINE_ROOT_PATH}",
        parameter_values={
            "raw_dataset_uri": MOOD_SAMPLES_URI,
            "mood_catalog_uri": MOOD_CATALOG_URI,
        },
    )
    job.submit()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
from google.cloud import aiplatform
from kfp import compiler
from src.pipelines.model_training_pipeline import model_training_pipeline

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION")
PIPELINE_ROOT = os.getenv("PIPELINE_ROOT", f"gs://{os.getenv('GCP_BUCKET_NAME')}/vertex_pipelines/")
GCS_INPUT_URI = os.getenv("GCS_INPUT_URI", "gs://bucketllmops/yoda_sentences.csv")

pipeline_package_path = "model_training_pipeline.json"

compiler.Compiler().compile(
	pipeline_func=model_training_pipeline,
	package_path=pipeline_package_path
)

aiplatform.init(project=PROJECT_ID, location=REGION)

job = aiplatform.PipelineJob(
    display_name="model-training-pipeline",
    template_path=pipeline_package_path,
    pipeline_root=PIPELINE_ROOT,
    parameter_values={
        "gcs_input_uri": GCS_INPUT_URI,
    },
    enable_caching=False,
)

job.run(service_account="vertex-ai-runner@lunar-byte-475017-r8.iam.gserviceaccount.com", sync=True)

print(f"Pipeline lancé ! Suivez ce lien pour voir l'exécution : {job.dashboard_uri}")

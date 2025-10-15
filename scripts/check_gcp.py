import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(Path(__file__).parent.parent / ".env")

project = os.getenv("GCP_PROJECT_ID")
region = os.getenv("GCP_REGION")
bucket = os.getenv("GCP_BUCKET_NAME")

print(f"[CHECK] GCP_PROJECT_ID: {project}")
print(f"[CHECK] GCP_REGION: {region}")
print(f"[CHECK] GCP_BUCKET_NAME: {bucket}")

from google.cloud import aiplatform, storage

# Vérifier l'initialisation du client Vertex AI
try:
	aiplatform.init(project=project, location=region)
	print("[CHECK] Vertex AI client initialized successfully.")
except Exception as e:
	print(f"[FAIL] Vertex AI client initialization failed: {e}")

# Vérifier l'accès au bucket GCS
try:
	storage_client = storage.Client(project=project)
	blobs = list(storage_client.list_blobs(bucket))
	print(f"[CHECK] {len(blobs)} objets trouvés dans le bucket '{bucket}'")
except Exception as e:
	print(f"[FAIL] GCS bucket access failed: {e}")

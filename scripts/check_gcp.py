import os
import sys


def fail(msg, code=1):
    print(f"ERROR: {msg}")
    sys.exit(code)


def main():
    project = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION")
    bucket = os.getenv("GCP_BUCKET_NAME")

    if not project or not region or not bucket:
        missing = [k for k, v in [("GCP_PROJECT_ID", project), ("GCP_REGION", region), ("GCP_BUCKET_NAME", bucket)] if not v]
        fail(f"Missing environment variables: {', '.join(missing)}", code=2)

    print(f"Using project={project}, region={region}, bucket={bucket}")

    # Check Vertex AI initialization
    try:
        from google.cloud import aiplatform
    except Exception as e:
        fail(f"Unable to import google.cloud.aiplatform: {e}", code=3)

    try:
        aiplatform.init(project=project, location=region)
        print("Vertex AI client initialized successfully.")
    except Exception as e:
        fail(f"Failed to init Vertex AI client: {e}", code=4)

    # Check GCS access
    try:
        from google.cloud import storage
    except Exception as e:
        fail(f"Unable to import google.cloud.storage: {e}", code=5)

    try:
        storage_client = storage.Client(project=project)
        bucket_obj = storage_client.get_bucket(bucket)
        blobs = list(storage_client.list_blobs(bucket))
        print(f"Found {len(blobs)} object(s) in bucket '{bucket}':")
        for b in blobs[:20]:
            print(f" - {b.name} ({b.size} bytes)")
        if len(blobs) > 20:
            print(f"  ... and {len(blobs)-20} more objects")
    except Exception as e:
        fail(f"Failed to access GCS bucket '{bucket}': {e}", code=6)

    print("GCP setup check finished successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

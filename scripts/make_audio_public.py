import os
from pathlib import Path
from typing import Optional

import typer
from google.cloud import storage

from src.constants import BUCKET_NAME, PROJECT_ID


def _load_dotenv() -> None:
    """Best-effort load of .env so the script works outside Chainlit."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def make_audio_public():
    """Make all audio files in the bucket publicly accessible"""
    
    project_id: Optional[str] = os.getenv("GCP_PROJECT_ID") or PROJECT_ID
    bucket_name: Optional[str] = os.getenv("GCP_BUCKET_NAME") or BUCKET_NAME
    
    if not project_id or not bucket_name:
        raise ValueError(
            "GCP_PROJECT_ID and GCP_BUCKET_NAME must be set in the environment or .env file."
        )

    print(f"Project: {project_id}")
    print(f"Bucket: {bucket_name}")
    
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.get_bucket(bucket_name)
    
    # Check if bucket uses uniform access
    if bucket.iam_configuration.uniform_bucket_level_access_enabled:
        print("\nBucket uses uniform access. Setting public-read on bucket level...")
        policy = bucket.get_iam_policy(requested_policy_version=3)
        policy.bindings.append({
            "role": "roles/storage.objectViewer",
            "members": {"allUsers"}
        })
        bucket.set_iam_policy(policy)
        print("✅ Bucket is now publicly readable")
    
    # List all files in audio_previews directory
    blobs = bucket.list_blobs(prefix="audio_previews/")
    
    audio_files = [blob for blob in blobs if blob.name.endswith(".mp3")]
    print(f"\nFound {len(audio_files)} audio files")
    
    for blob in audio_files:
        print(f"✅ {blob.name}")
        print(f"   URL: {blob.public_url}")
    
    print(f"\n🎵 All {len(audio_files)} audio files are now publicly accessible!")


if __name__ == "__main__":
    _load_dotenv()
    typer.run(make_audio_public)

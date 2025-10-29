# 🎵 Synesthetic DJ

> An AI-powered system that generates personalized music and lighting recommendations based on emotional state descriptions.

**Created by:** Enzo Berreur & Elea Nizam

[View slides (PDF)](LLMops_FinalPresentation.pdf)
---

## 📖 Overview

**Synesthetic DJ** is a machine learning project that bridges the gap between textual descriptions of emotions and multisensory ambient experiences. The system analyzes natural language input describing a user's mood and generates:

- **Music recommendations** from a curated catalog of 12 emotional soundscapes
- **Dynamic lighting sequences** with RGB color palettes, durations, and intensity levels
- **Narrative descriptions** that contextualize the generated ambiance

### The Concept

The name "Synesthetic DJ" draws inspiration from synesthesia—a neurological phenomenon where stimulation of one sensory pathway leads to automatic experiences in another. Our system creates this cross-sensory mapping by training a language model to understand emotional descriptions and translate them into coordinated audio-visual recommendations.

---

## 🧠 How It Works

### Architecture

The project leverages a **fine-tuned Phi-3-mini-4k-instruct** model with LoRA (Low-Rank Adaptation) adapters, trained on a custom dataset of ~520 examples mapping emotional descriptions to mood profiles.

#### Input
Natural language description of emotional state:
```
"Je me sens joyeux ce matin et je veux une ambiance solaire"
```

#### Output
Structured JSON response containing:
```json
{
  "track": {
    "mood_id": "bonnehumeur",
    "preview_uri": "gs://llmops-enzo/audio_previews/Bonnehumeur.mp3"
  },
  "lighting": [
    {"rgb": [255, 210, 140], "duration": 12, "intensity": 0.55},
    {"rgb": [250, 235, 180], "duration": 8, "intensity": 0.45}
  ],
  "narration": "Ambiance solaire et détendue pour entretenir cette bonne humeur.",
  "diagnostics": {
    "valence_hint": 0.9,
    "arousal_hint": 0.4
  }
}
```

### Machine Learning Pipeline

The project implements a complete MLOps workflow using **Google Cloud Vertex AI Pipelines**:

1. **Data Transformation Component** (`data_transformation_component.py`)
   - Loads raw mood samples and catalog data from GCS
   - Applies chat templates to format training examples
   - Splits data into train/test sets (90/10 split)
   - Outputs prepared datasets for downstream tasks

2. **Fine-Tuning Component** (`fine_tuning_component.py`)
   - Fine-tunes microsoft/Phi-3-mini-4k-instruct using LoRA
   - Configured for NVIDIA T4 GPU acceleration
   - Produces an adapted model optimized for mood-to-ambiance generation

3. **Inference Component** (`inference_component.py`)
   - Runs batch predictions on the test dataset
   - Generates structured JSON outputs for evaluation
   - Handles output parsing and error recovery

4. **Evaluation Component** (`evaluation_component.py`)
   - Computes BLEU and ROUGE metrics
   - Provides quantitative assessment of model quality
   - Current performance: **BLEU: 0.258 | ROUGE: 0.520**

### Mood Catalog

The system recognizes **12 distinct emotional states**, each mapped to curated audio tracks and lighting profiles:

| Mood | Description |
|------|-------------|
| **bonnehumeur** | Ambiance solaire et détendue |
| **curiosite** | Mouvement malicieux et lumineux |
| **detente** | Ondes bleues et calmes |
| **euphorie** | Flux explosif et lumineux |
| **reverie** | Atmosphère suspendue cosmique |
| **victoire** | Éclat victorieux |
| **colere** | Cadence intense |
| **inquietude** | Pulsations feutrées |
| **nostalgie** | Teintes sépia et rythme doux |
| **panique** | Impacts rapides |
| **suspense** | Texture feutrée |
| **tristesse** | Halo discret et consolant |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11.6 (exact version required)
- [uv](https://github.com/astral-sh/uv) package manager
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- A GCP project with Vertex AI enabled

### Step 1: Installation

**Install dependencies and create virtual environment:**
```bash
uv venv
uv sync
```

**Activate the virtual environment:**
```bash
source .venv/bin/activate
```

### Step 2: GCP Authentication

**Authenticate with Google Cloud:**
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

**Enable required GCP APIs:**
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### Step 3: Environment Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and fill in your values:**
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_PROJECT_NUMBER`: Your GCP project number
   - `GCP_BUCKET_NAME`: Your GCS bucket name
   - `GCP_REGION`: Deployment region (e.g., `europe-west2`)
   - Upload mood datasets (`mood_samples.csv` and `mood_catalog.csv`) to your GCS bucket

3. **Load environment variables:**
   ```bash
   export $(cat .env | xargs)
   ```

### Step 4: Training Pipeline (Optional)

If you need to train a new model from scratch:

```bash
source .venv/bin/activate
export $(cat .env | xargs)
PYTHONPATH=. python scripts/pipeline_runner.py
```

This orchestrates: data transformation → fine-tuning → inference → evaluation (takes ~2-3 hours with GPU).

### Step 5: Model Deployment

**A. List available models in Vertex AI:**
```bash
source .venv/bin/activate
export $(cat .env | xargs)
python -c "
from google.cloud import aiplatform
from src.constants import PROJECT_ID, REGION

aiplatform.init(project=PROJECT_ID, location=REGION)
models = aiplatform.Model.list()

for i, model in enumerate(models, 1):
    print(f'{i}. {model.display_name}')
    print(f'   Resource: {model.resource_name}')
    print()
"
```

**B. Deploy your model to an endpoint:**

Replace `MODEL_RESOURCE_NAME` with the resource name from step A (e.g., `projects/54825872111/locations/europe-west2/models/9017459897251397632`):

```bash
source .venv/bin/activate
export $(cat .env | xargs)
python scripts/deploy_model.py "MODEL_RESOURCE_NAME"
```

⏱️ **Deployment takes ~10-15 minutes**

**C. After deployment completes:**

The script will output an **Endpoint ID**. Copy it and update your `.env` file:
```bash
GCP_ENDPOINT_ID=your_new_endpoint_id_here
```

**D. Verify deployment status:**
```bash
source .venv/bin/activate
export $(cat .env | xargs)
python scripts/check_endpoint_status.py YOUR_ENDPOINT_ID
```

### Step 6: Test the Endpoint

Once deployed, test the endpoint with a sample mood description:

```bash
source .venv/bin/activate
export $(cat .env | xargs)
python scripts/test_endpoint.py YOUR_ENDPOINT_ID \
  --test-input "Je me sens euphorique après avoir gagné la compétition"
```

---

## 🎨 Interactive Application

The project includes a **Chainlit-based web interface** (`src/app/synesthetic_dj.py`) that provides an immersive user experience:

- **Chat interface** for natural language mood descriptions
- **Audio playback** with automatic track streaming from GCS
- **Dynamic lighting animations** rendered as CSS animations with radial gradients and glow effects
- **Real-time narration** explaining the generated ambiance

### Launch the Chainlit App

**Prerequisites:** Make sure your model is deployed and `GCP_ENDPOINT_ID` is set in `.env`

```bash
source .venv/bin/activate
export $(cat .env | xargs)
PYTHONPATH=. chainlit run src/app/synesthetic_dj.py --port 8000
```

Then open your browser at: **http://localhost:8000**

The app features:
- 🎭 Starter prompts for common moods (Bonne humeur, Tristesse, Euphorie, Détente)
- 🎨 Immersive lighting overlays synchronized with audio
- 🎵 Audio preview playback from GCS
- ✨ Graceful error handling and loading states
- 🔄 Support for both GCS and HTTP audio sources

### Quick Start Commands

After initial setup, use these commands to launch the app:

```bash
cd "/path/to/llmops_final"
source .venv/bin/activate
export $(cat .env | xargs)
PYTHONPATH=. chainlit run src/app/synesthetic_dj.py --port 8000
```

---

## 📊 Technical Stack

- **ML Framework:** Hugging Face Transformers, PEFT (LoRA), TRL
- **Base Model:** microsoft/Phi-3-mini-4k-instruct
- **Cloud Infrastructure:** Google Cloud Vertex AI (Pipelines, Model Registry, Endpoints)
- **Pipeline Orchestration:** Kubeflow Pipelines (KFP)
- **Storage:** Google Cloud Storage
- **Web Framework:** Chainlit
- **Data Processing:** Pandas, Datasets
- **Evaluation:** ROUGE Score, SacreBLEU

---

## 📁 Project Structure

```
.
├── src/
│   ├── app/
│   │   ├── main.py                    # Legacy Chainlit app (Yoda LLM)
│   │   └── synesthetic_dj.py          # Synesthetic DJ Chainlit app
│   ├── pipeline_components/
│   │   ├── data_transformation_component.py
│   │   ├── fine_tuning_component.py
│   │   ├── inference_component.py
│   │   └── evaluation_component.py
│   ├── pipelines/
│   │   └── model_training_pipeline.py  # KFP pipeline definition
│   ├── constants.py                    # Project-wide constants
│   └── handler.py                      # Custom prediction handler
├── scripts/
│   ├── pipeline_runner.py              # Execute training pipeline
│   ├── deploy_model.py                 # Deploy model to endpoint
│   ├── test_endpoint.py                # Test deployed endpoint
│   ├── check_endpoint_status.py        # Monitor deployment status
│   ├── register_model_with_custom_handler.py
│   ├── make_audio_public.py            # Manage GCS audio permissions
│   └── validate_gcp_setup.py           # Verify GCP configuration
├── data/
│   ├── mood_catalog.csv                # Mood definitions
│   └── mood_samples.csv                # Training examples
├── audio/                              # Local audio preview files
├── chainlit.md                         # Chainlit app documentation
├── GUIDE.md                            # Deployment guide
└── pyproject.toml                      # Python dependencies
```

---

## 🎯 Future Enhancements

- **Expanded mood catalog** with more granular emotional states
- **Real-time audio generation** using generative audio models
- **Hardware integration** for physical smart lighting control (Philips Hue, etc.)
- **Multilingual support** for mood descriptions
- **User feedback loop** to continuously improve recommendations
- **Temporal awareness** to adapt ambiances based on time of day

---

## 📄 License

This project was developed as part of the LLMOps curriculum at Albert School.




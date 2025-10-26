# 🎵 Synesthetic DJ

> An AI-powered system that generates personalized music and lighting recommendations based on emotional state descriptions.

**Created by:** Enzo Berreur & Elea Nizam

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

### Installation

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required GCP APIs:**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable storage-component.googleapis.com
   gcloud services enable cloudresourcemanager.googleapis.com
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your project-specific values (project ID, region, bucket names, endpoint ID)
   - Upload mood datasets to your GCS bucket

### Running the Pipeline

To execute the full training pipeline:

```bash
export $(cat .env | xargs)
PYTHONPATH=. uv run python scripts/pipeline_runner.py
```

This will orchestrate the complete workflow: data transformation → fine-tuning → inference → evaluation.

### Deploying the Model

1. **Register the model with custom handler:**
   ```bash
   PYTHONPATH=. uv run python scripts/register_model_with_custom_handler.py
   ```

2. **Deploy to Vertex AI endpoint:**
   ```bash
   PYTHONPATH=. uv run python scripts/deploy_model.py
   ```

3. **Check deployment status:**
   ```bash
   PYTHONPATH=. uv run python scripts/check_endpoint_status.py
   ```

### Testing the Endpoint

Once deployed (deployment takes ~10-15 minutes), test with:

```bash
export $(cat .env | xargs)
PYTHONPATH=. uv run python scripts/test_endpoint.py YOUR_ENDPOINT_ID \
  --test-input "Je me sens euphorique après avoir gagné la compétition"
```

---

## 🎨 Interactive Application

The project includes a **Chainlit-based web interface** (`src/app/synesthetic_dj.py`) that provides an immersive user experience:

- **Chat interface** for natural language mood descriptions
- **Audio playback** with automatic track streaming from GCS
- **Dynamic lighting animations** rendered as CSS animations with radial gradients and glow effects
- **Real-time narration** explaining the generated ambiance

### Launch the app:

```bash
export $(cat .env | xargs)
PYTHONPATH=. uv run chainlit run src/app/synesthetic_dj.py
```

The app features:
- Starter prompts for common moods
- Immersive lighting overlays synchronized with audio
- Graceful error handling and loading states
- Support for both GCS and HTTP audio sources

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

---

## 👥 Authors

**Enzo Berreur** & **Elea Nizam**

*Albert School - Year 2 | 2025*

# Guide d'Utilisation - Synesthetic DJ Model

## 📊 Résumé du Projet

Le modèle **Synesthetic DJ** est un système qui génère des recommandations d'ambiance musicale et lumineuse basées sur l'état émotionnel de l'utilisateur.

### Input
Description textuelle de l'humeur (ex: "Je me sens joyeux ce matin")

### Output (JSON)
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

## 🎯 Étapes Complétées

1. ✅ Pipeline de fine-tuning exécuté
2. ✅ Modèle enregistré dans Vertex AI
3. ⏳ Déploiement sur endpoint (en cours)

## 🚀 Prochaines Étapes

### 1. Vérifier le statut du déploiement

```bash
cd /Users/enzoberreur/Downloads/session5_code
export $(cat .env | xargs)
PYTHONPATH=. uv run python -c "
from google.cloud import aiplatform
from src.constants import PROJECT_ID, REGION
aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint('3267779344075849728')
print(f'Endpoint: {endpoint.display_name}')
print(f'State: {endpoint.gca_resource.deployed_models}')
"
```

### 2. Tester le modèle

Une fois le déploiement terminé (~10-15 min):

```bash
export $(cat .env | xargs)
PYTHONPATH=. uv run python scripts/test_endpoint.py 3267779344075849728
```

Ou avec votre propre texte:

```bash
export $(cat .env | xargs)
PYTHONPATH=. uv run python scripts/test_endpoint.py 3267779344075849728 \
  --test-input "Je suis triste ce soir"
```

### 3. Mettre à jour .env avec l'Endpoint ID

Ajouter dans `.env`:
```
GCP_ENDPOINT_ID=3267779344075849728
```

### 4. Lancer l'application Chainlit

L'application Chainlit (`src/app/main.py`) fournit une interface chat pour interagir avec le modèle.

**Important**: Mettre à jour `src/app/main.py` pour adapter au projet Synesthetic DJ (actuellement configuré pour "Yoda LLM").

```bash
export $(cat .env | xargs)
PYTHONPATH=. uv run chainlit run src/app/main.py
```

## 📝 Moods Disponibles

Le modèle reconnaît 12 humeurs:
- **bonnehumeur** - Ambiance solaire et détendue
- **curiosite** - Mouvement malicieux et lumineux
- **detente** - Ondes bleues et calmes
- **euphorie** - Flux explosif et lumineux
- **reverie** - Atmosphère suspendue cosmique
- **victoire** - Éclat victorieux
- **colere** - Cadence intense
- **inquietude** - Pulsations feutrées
- **nostalgie** - Teintes sépia et rythme doux
- **panique** - Impacts rapides
- **suspense** - Texture feutrée
- **tristesse** - Halo discret et consolant

## 🔧 Métriques du Modèle

- **BLEU Score**: 0.258 (26%)
- **ROUGE Score**: 0.520 (52%)
- **Architecture**: Phi-3-mini-4k-instruct + LoRA
- **Dataset**: ~520 exemples d'entraînement

## 📚 Resources

- Model Registry: [Console GCP](https://console.cloud.google.com/vertex-ai/models?project=llm-ops-475209)
- Endpoints: [Console GCP](https://console.cloud.google.com/vertex-ai/endpoints?project=llm-ops-475209)
- Pipeline Runs: [Console GCP](https://console.cloud.google.com/vertex-ai/pipelines?project=llm-ops-475209)

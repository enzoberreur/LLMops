# LLMOps

## Description

Ce projet est un framework pour les opérations de machine learning (MLOps) spécialement conçu pour les grands modèles de langage (LLM). Il utilise Google Cloud Platform pour déployer, gérer et surveiller des modèles d'IA.

## Fonctionnalités

- Intégration avec Google Cloud AI Platform
- Gestion des données avec BigQuery
- Stockage des modèles avec Google Cloud Storage
- Pipeline MLOps pour les LLM

## Prérequis

- Python >= 3.9
- Compte Google Cloud Platform avec les APIs activées :
  - AI Platform API
  - BigQuery API
  - Cloud Storage API

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/enzoberreur/LLMops.git
cd LLMops
```

2. Installez les dépendances :
```bash
pip install -e .
```

## Configuration

1. Configurez l'authentification Google Cloud :
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. Assurez-vous que les APIs nécessaires sont activées dans votre projet GCP.

## Utilisation

Exécutez le script principal :
```bash
python main.py
```

## Structure du projet

```
LLMops/
├── main.py           # Point d'entrée principal
├── pyproject.toml    # Configuration du projet et dépendances
└── README.md         # Ce fichier
```

## Dépendances

- `google-cloud-aiplatform` >= 1.120.0 - Intégration AI Platform
- `google-cloud-bigquery` >= 3.38.0 - Gestion des données
- `google-cloud-storage` >= 2.19.0 - Stockage cloud

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## Licence

[Ajoutez votre licence ici]

## Auteur

Enzo Berreur
Elea Nizam
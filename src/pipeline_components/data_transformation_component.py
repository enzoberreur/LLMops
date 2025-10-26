"""Data transformation component for Vertex AI pipeline."""

from kfp.dsl import OutputPath, component


@component(
    base_image="python:3.11-slim",
    packages_to_install=[
        "pandas>=2.3.2",
        "datasets==4.0.0",
        "gcsfs",
    ],
)
def data_transformation_component(
    raw_dataset_uri: str,
    mood_catalog_uri: str,
    train_test_split_ratio: float,
    train_dataset: OutputPath("Dataset"),  # type: ignore
    test_dataset: OutputPath("Dataset"),  # type: ignore
) -> None:
    """Prepare Synesthetic DJ training pairs and split them for fine-tuning."""
    import json
    import logging

    import pandas as pd
    from datasets import Dataset

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting data transformation process...")

    logger.info(f"Loading mood samples from {raw_dataset_uri}")
    samples_df = pd.read_csv(raw_dataset_uri)
    logger.info(f"Loading mood catalog from {mood_catalog_uri}")
    catalog_df = pd.read_csv(mood_catalog_uri)

    dataset_df = samples_df.merge(catalog_df, on="mood_id", how="left")
    if dataset_df["file_uri"].isna().any():
        missing = dataset_df[dataset_df["file_uri"].isna()]["mood_id"].unique()
        raise ValueError(f"Missing audio preview for moods: {missing}")

    mood_narrations = {
        "bonnehumeur": "Ambiance solaire et detendue pour entretenir cette bonne humeur.",
        "curiosite": "Mouvement malicieux et lumineux pour soutenir ta curiosite.",
        "detente": "Ondes bleutees et calmes pour prolonger ta detente.",
        "euphorie": "Flux explosif et lumineux qui accompagne ton euphorie.",
        "reverie": "Atmosphere suspendue propice a la reverie cosmique.",
        "victoire": "Eclat victorieux pour celebrer cette reussite.",
        "colere": "Cadence intense pour canaliser et relacher la colere.",
        "inquietude": "Pulsations feutrees pour apprivoiser cette inquietude.",
        "nostalgie": "Teintes sepie et rythme doux pour ta nostalgie.",
        "panique": "Impacts rapides pour te guider dans la panique.",
        "suspense": "Texture feutree pour soutenir le suspense qui monte.",
        "tristesse": "Halo discret et consolant pour accueillir la tristesse.",
    }

    mood_metrics = {
        "bonnehumeur": {"valence": 0.9, "arousal": 0.4},
        "curiosite": {"valence": 0.6, "arousal": 0.6},
        "detente": {"valence": 0.7, "arousal": 0.3},
        "euphorie": {"valence": 0.95, "arousal": 0.85},
        "reverie": {"valence": 0.5, "arousal": 0.45},
        "victoire": {"valence": 0.85, "arousal": 0.75},
        "colere": {"valence": 0.2, "arousal": 0.8},
        "inquietude": {"valence": 0.35, "arousal": 0.55},
        "nostalgie": {"valence": 0.5, "arousal": 0.35},
        "panique": {"valence": 0.1, "arousal": 0.95},
        "suspense": {"valence": 0.4, "arousal": 0.6},
        "tristesse": {"valence": 0.15, "arousal": 0.3},
    }

    def build_assistant_payload(row: pd.Series) -> str:
        """Create assistant JSON payload embedding audio and lighting instructions."""
        lighting = json.loads(row["lighting_script"])
        narration = mood_narrations.get(
            row["mood_id"], "Ambiance personnalisee pour ton humeur."
        )
        metrics = mood_metrics.get(
            row["mood_id"], {"valence": 0.5, "arousal": 0.5}
        )
        payload = {
            "track": {
                "mood_id": row["mood_id"],
                "preview_uri": row["file_uri"],
            },
            "lighting": lighting,
            "narration": narration,
            "diagnostics": {
                "valence_hint": metrics["valence"],
                "arousal_hint": metrics["arousal"],
            },
        }
        return json.dumps(payload, ensure_ascii=True)

    logger.info("Building structured messages...")
    dataset_df["messages"] = dataset_df.apply(
        lambda row: [
            {"role": "user", "content": row["user_text"]},
            {"role": "assistant", "content": build_assistant_payload(row)},
        ],
        axis=1,
    )

    formatted_dataset = Dataset.from_pandas(
        dataset_df[["messages"]], preserve_index=False
    )
    logger.info(
        "Splitting dataset into train/test with ratio %.2f",
        train_test_split_ratio,
    )
    split_dataset = formatted_dataset.train_test_split(
        test_size=train_test_split_ratio, shuffle=True, seed=42
    )

    logger.info("Writing train dataset to %s", train_dataset)
    split_dataset["train"].to_csv(train_dataset, index=False)

    logger.info("Writing test dataset to %s", test_dataset)
    split_dataset["test"].to_csv(test_dataset, index=False)

    logger.info("Data transformation process completed successfully")


from kfp.dsl import pipeline
from src.pipeline_components.data_transformation_component import data_transformation_component

@pipeline(name="model-training-pipeline")
def model_training_pipeline(
    gcs_input_uri: str,
    test_size: float = 0.2,
    seed: int = 42,
):
    data_transformation_component(
        gcs_input_uri=gcs_input_uri,
        test_size=test_size,
        seed=seed,
    )

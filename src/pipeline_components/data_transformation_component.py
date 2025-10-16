
from kfp.dsl import component, OutputPath
import logging

@component(
	base_image="python:3.11",
	packages_to_install=["pandas", "datasets", "gcsfs", "python-dotenv"]
)
def data_transformation_component(
	gcs_input_uri: str,
	train_output_path: OutputPath(str),
	test_output_path: OutputPath(str),
	test_size: float = 0.2,
	seed: int = 42,
):
	import pandas as pd
	from datasets import Dataset
	import logging

	logging.basicConfig(level=logging.INFO)
	logging.info(f"Lecture du dataset depuis {gcs_input_uri}")

	df = pd.read_csv(gcs_input_uri)
	hf_dataset = Dataset.from_pandas(df)

	def format_dataset(examples):
		if isinstance(examples["prompt"], list):
			output_texts = []
			for i in range(len(examples["prompt"])):
				converted_sample = [
					{"role": "user", "content": examples["prompt"][i]},
					{"role": "assistant", "content": examples["completion"][i]},
				]
				output_texts.append(converted_sample)
			return {'messages': output_texts}
		else:
			converted_sample = [
				{"role": "user", "content": examples["prompt"]},
				{"role": "assistant", "content": examples["completion"]},
			]
			return {'messages': converted_sample}

	dataset = hf_dataset.rename_column("sentence", "prompt")
	dataset = dataset.rename_column("translation_extra", "completion")
	dataset = dataset.map(format_dataset)
	dataset = dataset.remove_columns(['prompt', 'completion', 'translation'])

	split = dataset.train_test_split(test_size=test_size, seed=seed)
	train_dataset = split['train']
	test_dataset = split['test']

	logging.info(f"Export du train vers {train_output_path}")
	train_dataset.to_csv(train_output_path)
	logging.info(f"Export du test vers {test_output_path}")
	test_dataset.to_csv(test_output_path)

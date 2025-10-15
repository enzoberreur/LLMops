import pandas as pd
from datasets import Dataset
import os
from dotenv import load_dotenv


gcs_uri = f"gs://bucketllmops/yoda_sentences.csv" 
df = pd.read_csv(gcs_uri)

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

split = dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = split['train']
test_dataset = split['test']

train_dataset.to_csv("train.csv")
test_dataset.to_csv("test.csv")

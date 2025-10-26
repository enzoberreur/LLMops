"""Script to test the deployed model endpoint."""

import json
import subprocess

import typer
from google.cloud import aiplatform
from transformers import AutoTokenizer

from src.constants import PROJECT_ID, REGION

MODEL_REPO_ID = "microsoft/Phi-3-mini-4k-instruct"


def build_prompt(tokenizer: AutoTokenizer, sentence: str):
    """Build a prompt from a sentence applying the chat template."""
    return tokenizer.apply_chat_template(
        [
            {"role": "user", "content": sentence},
        ],
        tokenize=False,
        add_generation_prompt=True,
    )


def test_endpoint(
    endpoint_id: str,
    test_input: str = "Je me sens incroyablement positif ce matin et je veux une ambiance qui danse facilement.",
):
    """Test the deployed model endpoint with a sample input."""
    aiplatform.init(project=PROJECT_ID, location=REGION)

    # Get the endpoint
    endpoint = aiplatform.Endpoint(
        f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{endpoint_id}"
    )
    print(f"Testing endpoint: {endpoint.display_name}")
    print(f"Endpoint ID: {endpoint_id}")
    print()

    # Prepare the input
    tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO_ID)
    prompt = build_prompt(tokenizer, test_input)

    print(f"Test input: {test_input}")
    print()

    # Make prediction
    print("Sending prediction request...")
    instances = [{"input": prompt}]
    parameters = {"max_new_tokens": 256}

    try:
        response = endpoint.predict(instances=instances, parameters=parameters)
        
        print("✅ Prediction successful!")
        print()
        print("Raw response:")
        print(response.predictions[0])
        print()
        
        # Try to extract and format JSON
        try:
            import re
            # Extract JSON between <|assistant|> and <|end|>
            json_match = re.search(r'<\|assistant\|>\s*(.*?)\s*<\|end\|>', response.predictions[0], re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                # Remove extra closing brace if present
                if json_str.count('}') > json_str.count('{'):
                    json_str = json_str[:-1]
                parsed = json.loads(json_str)
                print("Parsed JSON response:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            else:
                print("Could not extract JSON from response")
        except Exception as e:
            print(f"Could not parse JSON: {e}")
            
    except Exception as e:
        print(f"❌ Prediction failed: {e}")


if __name__ == "__main__":
    typer.run(test_endpoint)

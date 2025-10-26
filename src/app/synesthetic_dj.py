"""Chainlit app for Synesthetic DJ with audio and lighting effects."""

import json
import re
import subprocess
from typing import Optional

import chainlit as cl
import requests
from chainlit.message import Message
from google.cloud import storage
from transformers import AutoTokenizer

from src.constants import ENDPOINT_ID, PROJECT_NUMBER, REGION

MODEL_REPO_ID = "microsoft/Phi-3-mini-4k-instruct"
ENDPOINT_URL = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}:predict"
_storage_client: Optional[storage.Client] = None
_AUDIO_BLOB_OVERRIDES = {
    "audio_previews/Bonnehumeur.mp3": "audio_previews/BonneHumeur.mp3",
    "audio_previews/Tristess.mp3": "audio_previews/Tristesse.mp3",
}


def _get_storage_client() -> storage.Client:
    """Lazily instantiate the Cloud Storage client."""
    global _storage_client  # noqa: PLW0603
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


@cl.set_starters  # type: ignore
async def set_starters():
    """Set starter messages for the Chainlit app."""
    return [
        cl.Starter(
            label="😊 Bonne humeur",
            message="Je me sens incroyablement positif ce matin et je veux une ambiance solaire",
        ),
        cl.Starter(
            label="😢 Tristesse",
            message="Je me sens triste ce soir",
        ),
        cl.Starter(
            label="🎉 Euphorie",
            message="Je suis euphorique après avoir gagné la compétition",
        ),
        cl.Starter(
            label="😌 Détente",
            message="Je veux dissoudre la fatigue dans un bain chaud",
        ),
    ]


def build_prompt(tokenizer: AutoTokenizer, sentence: str) -> str:
    """Build a prompt from a sentence applying the chat template."""
    return tokenizer.apply_chat_template(  # type: ignore
        [
            {"role": "user", "content": sentence},
        ],
        tokenize=False,
        add_generation_prompt=True,
    )


def extract_json_response(generated_text: str) -> dict:
    """Extract and parse JSON response from the generated text."""
    # Extract JSON between <|assistant|> and <|end|>
    json_match = re.search(
        r"<\|assistant\|>\s*(.*?)\s*<\|end\|>", generated_text, re.DOTALL
    )
    if json_match:
        json_str = json_match.group(1).strip()
        # Remove extra closing brace if present (model sometimes adds one)
        if json_str.count("}") > json_str.count("{"):
            json_str = json_str[:-1]
        return json.loads(json_str)
    raise ValueError("Could not extract JSON from response")


def call_model_api(message: str) -> dict:
    """Call the Synesthetic DJ model API."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO_ID)

    access_token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()

    templated_input = build_prompt(tokenizer, message)
    model_input = {
        "instances": [{"input": templated_input}],
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.1,
            "top_p": 0.8,
        },
    }

    response = requests.post(
        ENDPOINT_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=model_input,
        timeout=30,
    ).json()

    raw_response = response["predictions"][0]
    return extract_json_response(raw_response)


def rgb_to_hex(rgb: list[int]) -> str:
    """Convert RGB list to hex color."""
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def rgb_to_rgba(rgb: list[int], alpha: float) -> str:
    """Convert RGB list to rgba() string with bounded alpha."""
    bounded_alpha = max(0.0, min(alpha, 1.0))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {bounded_alpha:.2f})"


def create_lighting_animation_html(lighting: list[dict]) -> str:
    """Create an immersive lighting animation overlay."""
    if not lighting:
        return ""

    background_frames: list[str] = []
    glow_frames: list[str] = []
    beam_frames: list[str] = []
    total_duration = sum(light["duration"] for light in lighting) or 1.0
    current_time = 0.0

    for light in lighting:
        percentage = (current_time / total_duration) * 100
        color = light["rgb"]
        intensity = float(light.get("intensity", 0.5))
        background_frames.append(
            f"{percentage:.1f}% {{ "
            f"background: radial-gradient(circle at 50% 50%, {rgb_to_rgba(color, min(0.85, max(0.25, intensity + 0.15)))} 0%, "
            "rgba(0, 0, 0, 0.1) 65%, rgba(0, 0, 0, 0.6) 100%); }}"
        )
        glow_frames.append(
            f"{percentage:.1f}% {{ "
            f"box-shadow: 0 0 {80 + int(intensity * 140)}px {rgb_to_rgba(color, min(0.75, intensity + 0.2))}; "
            f"opacity: {min(0.8, intensity + 0.15):.2f}; }}"
        )
        beam_frames.append(
            f"{percentage:.1f}% {{ "
            f"background: conic-gradient(from {percentage * 3.6:.1f}deg, {rgb_to_rgba(color, min(0.55, intensity + 0.05))} 15%, transparent 60%); "
            f"opacity: {min(0.45, intensity + 0.05):.2f}; }}"
        )
        current_time += light["duration"]

    first_light = lighting[0]
    first_color = first_light["rgb"]
    first_intensity = float(first_light.get("intensity", 0.5))
    background_frames.append(
        "100% { "
        f"background: radial-gradient(circle at 50% 50%, {rgb_to_rgba(first_color, min(0.85, max(0.25, first_intensity + 0.15)))} 0%, "
        "rgba(0, 0, 0, 0.1) 65%, rgba(0, 0, 0, 0.6) 100%); }}"
    )
    glow_frames.append(
        "100% { "
        f"box-shadow: 0 0 {80 + int(first_intensity * 140)}px {rgb_to_rgba(first_color, min(0.75, first_intensity + 0.2))}; "
        f"opacity: {min(0.8, first_intensity + 0.15):.2f}; }}"
    )
    beam_frames.append(
        "100% { "
        f"background: conic-gradient(from 360deg, {rgb_to_rgba(first_color, min(0.55, first_intensity + 0.05))} 15%, transparent 60%); "
        f"opacity: {min(0.45, first_intensity + 0.05):.2f}; }}"
    )

    return (
        "<style>"
        "@keyframes synDjBackground {"
        + " ".join(background_frames)
        + "}"
        "@keyframes synDjGlow {"
        + " ".join(glow_frames)
        + "}"
        "@keyframes synDjBeam {"
        + " ".join(beam_frames)
        + "}"
        "#synesthetic-dj-lighting {"
        "position: fixed; top: 0; left: 0; width: 100%; height: 100%;"
        "pointer-events: none; z-index: -2; overflow: hidden;"
        f"animation: synDjBackground {total_duration}s ease-in-out infinite;"
        "background-size: cover;"
        "}"
        "#synesthetic-dj-lighting .syn-layer {"
        "position: absolute; inset: -25%; mix-blend-mode: screen;"
        "}"
        "#synesthetic-dj-lighting .syn-glow {"
        f"animation: synDjGlow {total_duration}s ease-in-out infinite;"
        "border-radius: 45%; filter: blur(80px);"
        "}"
        "#synesthetic-dj-lighting .syn-beam {"
        f"animation: synDjBeam {total_duration}s linear infinite;"
        "filter: blur(45px);"
        "}"
        "</style>"
        "<div id='synesthetic-dj-lighting'>"
        "<div class='syn-layer syn-glow'></div>"
        "<div class='syn-layer syn-beam'></div>"
        "</div>"
    )


def format_confirmation(response: dict) -> str:
    """Generate a concise confirmation sentence for the user."""
    friendly_names = {
        "bonnehumeur": "bonne humeur",
        "curiosite": "curiosite",
        "detente": "detente",
        "euphorie": "euphorie",
        "reverie": "reverie",
        "victoire": "victoire",
        "colere": "colere",
        "inquietude": "inquietude",
        "nostalgie": "nostalgie",
        "panique": "panique",
        "suspense": "suspense",
        "tristesse": "tristesse",
    }
    mood_id = response["track"]["mood_id"]
    ambiance = friendly_names.get(mood_id, mood_id)
    narration = response.get(
        "narration", "Ambiance personnalisee en cours, laisse-toi porter."
    )
    return f"Ok, j'ai capture ton ambiance {ambiance}. {narration}"


def load_audio_content(url: str) -> dict:
    """Return keyword arguments for cl.Audio based on the source URL."""
    if not url:
        return {}

    if url.startswith("gs://"):
        path = url.removeprefix("gs://")
        if "/" not in path:
            return {}
        bucket_name, blob_name = path.split("/", 1)
        canonical_blob_name = _AUDIO_BLOB_OVERRIDES.get(blob_name, blob_name)
        try:
            client = _get_storage_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            if not blob.exists():
                blob = bucket.blob(canonical_blob_name)
            data = blob.download_as_bytes()
            return {"content": data, "mime": "audio/mpeg"}
        except Exception as exc:  # pylint: disable=broad-except
            cl.logger.error("Failed to download audio %s (canonical %s): %s", url, canonical_blob_name, exc)
            return {}

    return {"url": url, "mime": "audio/mpeg"}


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    return None


@cl.on_message
async def handle_message(message: Message):
    """Handle incoming messages from the user."""
    # Show loading message
    loading_msg = cl.Message(content="🎧 Analyse de votre humeur en cours...")
    await loading_msg.send()

    try:
        # Call the model
        response = call_model_api(message.content)

        # Update loading message
        loading_msg.content = "✨ Génération de l'ambiance..."
        await loading_msg.update()

        # Prepare elements (lighting + audio)
        elements: list = []
        lighting_html = create_lighting_animation_html(response.get("lighting", []))
        if lighting_html:
            elements.append(
                cl.Text(
                    name="ambiance-lighting",
                    content=lighting_html,
                    display="page",
                    mime="text/html",
                )
            )

        audio_kwargs = load_audio_content(response["track"]["preview_uri"])
        if audio_kwargs:
            elements.append(
                cl.Audio(
                    name="ambiance-audio",
                    auto_play=True,
                    display="inline",
                    **audio_kwargs,
                )
            )

        # Remove loading message
        await loading_msg.remove()

        # Send concise confirmation message with elements
        confirmation = format_confirmation(response)
        await cl.Message(content=confirmation, elements=elements).send()

    except Exception as e:
        await loading_msg.remove()
        await cl.Message(
            content=f"❌ Erreur lors de l'analyse : {str(e)}\n\nVeuillez réessayer avec une autre description."
        ).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)

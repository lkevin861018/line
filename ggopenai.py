import base64
import os
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

_client = None


def openai_client():
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("chatgpt_api_key")
        _client = OpenAI(api_key=api_key) if api_key else OpenAI()
    return _client


def env_int(name, default):
    try:
        return max(0, int(os.getenv(name, default)))
    except ValueError:
        return default


BASE_DIR = Path(__file__).resolve().parent
GOOGLE_PROMPT_DOC_ID = "1eqIA-itJ7MvGSu0hF_8BAgnVqBq--81S9SMsHi5SLII"
GOOGLE_PROMPT_EXPORT_URL = (
    f"https://docs.google.com/document/d/{GOOGLE_PROMPT_DOC_ID}/export?format=txt"
)
DEFAULT_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.5")
DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
DEFAULT_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
DEFAULT_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "auto")
DEFAULT_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low")
DEFAULT_TEXT_VERBOSITY = os.getenv("OPENAI_TEXT_VERBOSITY", "medium")
MAX_HISTORY_MESSAGES = env_int("OPENAI_HISTORY_LIMIT", 20)
PROMPT_CACHE_SECONDS = env_int("GOOGLE_PROMPT_CACHE_SECONDS", 300)
PROMPT_FETCH_TIMEOUT_SECONDS = env_int("GOOGLE_PROMPT_FETCH_TIMEOUT_SECONDS", 10)

messages = []
_prompt_cache = {
    "content": None,
    "fetched_at": 0.0,
}


def system_instructions():
    now = time.time()
    cached_prompt = _prompt_cache["content"]
    cache_age = now - _prompt_cache["fetched_at"]
    if cached_prompt and cache_age < PROMPT_CACHE_SECONDS:
        return cached_prompt

    try:
        response = requests.get(GOOGLE_PROMPT_EXPORT_URL, timeout=PROMPT_FETCH_TIMEOUT_SECONDS)
        response.raise_for_status()
        prompt = response.text.strip()
        if not prompt or looks_like_html(prompt):
            raise ValueError("Google document export did not return plain text")
    except (requests.RequestException, ValueError) as exc:
        if cached_prompt:
            return cached_prompt
        raise RuntimeError("Failed to load prompt from Google document") from exc

    _prompt_cache["content"] = prompt
    _prompt_cache["fetched_at"] = now
    return prompt


def looks_like_html(text):
    lowered = text.lstrip().lower()
    return lowered.startswith("<!doctype html") or lowered.startswith("<html")


def cgpt(ask, gen=None):
    global messages

    model = gen or DEFAULT_CHAT_MODEL
    input_messages = messages + [{"role": "user", "content": ask}]
    request_args = {
        "model": model,
        "input": [
            {"role": "system", "content": system_instructions()},
            *input_messages,
        ],
        "reasoning": {"effort": DEFAULT_REASONING_EFFORT},
        "text": {"verbosity": DEFAULT_TEXT_VERBOSITY},
    }

    response = openai_client().responses.create(**request_args)

    answer = response.output_text.strip()
    messages.append({"role": "user", "content": ask})
    messages.append({"role": "assistant", "content": answer})
    if MAX_HISTORY_MESSAGES:
        messages = messages[-MAX_HISTORY_MESSAGES:]
    else:
        messages = []
    return answer


def igpt(req, output_dir=None):
    image_completion = openai_client().images.generate(
        model=DEFAULT_IMAGE_MODEL,
        prompt=req,
        size=DEFAULT_IMAGE_SIZE,
        quality=DEFAULT_IMAGE_QUALITY,
        n=1,
    )

    image_data = image_completion.data[0]
    image_bytes = _image_bytes(image_data)

    static_root = BASE_DIR / "static"
    generated_dir = Path(output_dir) if output_dir else static_root / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid.uuid4().hex}.png"
    output_path = generated_dir / file_name
    output_path.write_bytes(image_bytes)

    return f"generated/{file_name}"


def edit_image(image_path, prompt, output_dir=None):
    image_path = Path(image_path)
    with image_path.open("rb") as image_file:
        image_completion = openai_client().images.edit(
            model=DEFAULT_IMAGE_MODEL,
            image=image_file,
            prompt=prompt,
            size=DEFAULT_IMAGE_SIZE,
            quality=DEFAULT_IMAGE_QUALITY,
            n=1,
        )

    image_data = image_completion.data[0]
    image_bytes = _image_bytes(image_data)

    static_root = BASE_DIR / "static"
    edited_dir = Path(output_dir) if output_dir else static_root / "改圖"
    edited_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid.uuid4().hex}.png"
    output_path = edited_dir / file_name
    output_path.write_bytes(image_bytes)

    return f"改圖/{file_name}", output_path


def _image_bytes(image_data):
    if getattr(image_data, "b64_json", None):
        return base64.b64decode(image_data.b64_json)

    if getattr(image_data, "url", None):
        response = requests.get(image_data.url, timeout=30)
        response.raise_for_status()
        return response.content

    raise ValueError("OpenAI image response did not contain image data")

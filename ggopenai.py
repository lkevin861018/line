import base64
import os
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

_client = None
_grok_client = None


def openai_client():
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("chatgpt_api_key")
        _client = OpenAI(api_key=api_key) if api_key else OpenAI()
    return _client


def grok_client():
    global _grok_client

    if _grok_client is None:
        _grok_client = OpenAI(
            api_key=grok_api_key(),
            base_url=GROK_BASE_URL,
        )
    return _grok_client


def grok_api_key():
    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if api_key:
        return api_key.strip()

    raise RuntimeError("Grok API key not found. Set GROK_API_KEY in .env or environment variables.")


def env_int(name, default):
    try:
        return max(0, int(os.getenv(name, default)))
    except ValueError:
        return default


BASE_DIR = Path(__file__).resolve().parent
PROMPT_FILE = BASE_DIR / "prompt.txt"
GROK_BASE_URL = "https://api.x.ai/v1"
DEFAULT_GROK_MODEL = os.getenv("GROK_MODEL", "grok-4.3")
GROK_WEB_SEARCH_ENABLED = os.getenv("GROK_WEB_SEARCH_ENABLED", "true").lower() not in {
    "0",
    "false",
    "no",
    "off",
}
DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
DEFAULT_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
DEFAULT_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "auto")
DEFAULT_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low")
DEFAULT_TEXT_VERBOSITY = os.getenv("OPENAI_TEXT_VERBOSITY", "medium")
MAX_HISTORY_MESSAGES = env_int("OPENAI_HISTORY_LIMIT", 20)

messages = []


def system_instructions():
    if not PROMPT_FILE.exists():
        raise RuntimeError("prompt.txt not found")

    prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()
    if not prompt:
        raise RuntimeError("prompt.txt is empty")

    return prompt


def cgpt(ask, gen=None):
    global messages

    model = gen or DEFAULT_GROK_MODEL
    input_messages = messages + [{"role": "user", "content": ask}]
    request_args = {
        "model": model,
        "input": [
            {"role": "system", "content": system_instructions()},
            *input_messages,
        ],
    }
    if GROK_WEB_SEARCH_ENABLED:
        request_args["tools"] = [{"type": "web_search"}]

    response = grok_client().responses.create(**request_args)

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

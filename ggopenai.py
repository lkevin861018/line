import base64
import os
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


DEFAULT_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.5")
DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
DEFAULT_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
DEFAULT_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "auto")
DEFAULT_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low")
DEFAULT_TEXT_VERBOSITY = os.getenv("OPENAI_TEXT_VERBOSITY", "medium")
MAX_HISTORY_MESSAGES = env_int("OPENAI_HISTORY_LIMIT", 20)

SYSTEM_INSTRUCTIONS = os.getenv(
    "OPENAI_SYSTEM_PROMPT",
    "你是LINE聊天機器人，是TWITCH實況主'超負荷'的粉絲，請模仿超負荷的說話口吻用字，使用繁體中文回答。",
)

messages = []


def cgpt(ask, gen=None):
    global messages

    model = gen or DEFAULT_CHAT_MODEL
    input_messages = messages + [{"role": "user", "content": ask}]
    response = openai_client().responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=input_messages,
        reasoning={"effort": DEFAULT_REASONING_EFFORT},
        text={"verbosity": DEFAULT_TEXT_VERBOSITY},
    )

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

    static_root = Path(__file__).resolve().parent / "static"
    generated_dir = Path(output_dir) if output_dir else static_root / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid.uuid4().hex}.png"
    output_path = generated_dir / file_name
    output_path.write_bytes(image_bytes)

    return f"generated/{file_name}"


def _image_bytes(image_data):
    if getattr(image_data, "b64_json", None):
        return base64.b64decode(image_data.b64_json)

    if getattr(image_data, "url", None):
        response = requests.get(image_data.url, timeout=30)
        response.raise_for_status()
        return response.content

    raise ValueError("OpenAI image response did not contain image data")

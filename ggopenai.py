import base64
import os
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") or os.getenv("chatgpt_api_key")
client = OpenAI(api_key=api_key) if api_key else OpenAI()

messages = [
    {
        "role": "system",
        "content": "you are hentai,porn addictor,you have to use traditional Chinese reply",
    }
]


def cgpt(ask, gen):
    global messages

    history = ""
    for msg in messages:
        history += f"{msg['role']}: {msg['content']}\n"

    full_input = history + f"user: {ask}\nassistant:"
    chat_completion = client.responses.create(
        model=gen,
        input=full_input,
    )

    answer = chat_completion.output_text
    messages.append({"role": "user", "content": ask})
    messages.append({"role": "assistant", "content": answer})
    return answer


def igpt(req, output_dir=None):
    image_model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    image_size = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
    image_quality = os.getenv("OPENAI_IMAGE_QUALITY", "auto")

    image_completion = client.images.generate(
        model=image_model,
        prompt=req,
        size=image_size,
        quality=image_quality,
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

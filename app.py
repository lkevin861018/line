import json
import os
import random as rd

from dotenv import load_dotenv
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageSendMessage, MessageEvent, TextMessage, TextSendMessage
from openai import BadRequestError

import ggopenai


load_dotenv()

line_token = os.getenv("line_token") or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_secret = os.getenv("line_secret") or os.getenv("LINE_CHANNEL_SECRET")

app = Flask(__name__)
line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_secret)


def public_base_url():
    base_url = (
        os.getenv("APP_BASE_URL")
        or os.getenv("PUBLIC_BASE_URL")
        or os.getenv("RENDER_EXTERNAL_URL")
    )
    if base_url:
        return base_url.rstrip("/")

    render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_hostname:
        return f"https://{render_hostname.strip('/')}"

    return request.url_root.rstrip("/")


def static_url(path):
    return f"{public_base_url()}/static/{path.lstrip('/')}"


def image_message(static_path):
    image_url = static_url(static_path)
    return ImageSendMessage(
        original_content_url=image_url,
        preview_image_url=image_url,
    )


@app.route("/index", methods=["GET", "POST"])
def index():
    return "Hello World!!"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        events = json.loads(body).get("events", [])
    except json.JSONDecodeError as exc:
        app.logger.error("[ParseError] %s", exc)
        abort(400)

    for event in events:
        source = event.get("source", {})
        user_id = source.get("userId", "UnknownUser")
        group_id = source.get("groupId", "NoGroup")
        event_type = event.get("type", "")
        app.logger.info("[%s] Incoming event: %s group=%s", user_id, event_type, group_id)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    message = None

    if text == "銀河":
        message = image_message("boyvfv_is_dog.jpg")
    elif text == "抽":
        random_num = rd.randint(1, 134)
        message = image_message(f"roll/{random_num}_line.png")
    elif text.startswith("rolltest"):
        test_num = text[len("rolltest") :].strip()
        if not test_num.isdigit():
            message = TextSendMessage(text="請輸入 rolltest 編號，例如：rolltest 1")
        else:
            message = image_message(f"roll/{test_num}_line.png")
    elif text.startswith("@GG人畫圖"):
        prompt = text[len("@GG人畫圖") :].strip()
        if not prompt:
            message = TextSendMessage(text="請輸入想畫的內容")
        else:
            try:
                static_path = ggopenai.igpt(prompt)
                message = image_message(static_path)
            except BadRequestError:
                message = TextSendMessage(text="我是政確的狗汪汪!")
            except Exception as exc:
                app.logger.exception("OpenAI image generation failed: %s", exc)
                message = TextSendMessage(text="畫圖失敗，晚點再試一次")
    elif text.startswith("@GG人"):
        ask = text[len("@GG人") :].strip()
        if not ask:
            message = TextSendMessage(text="請輸入想問的內容")
        else:
            try:
                model = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")
                message = TextSendMessage(text=ggopenai.cgpt(ask=ask, gen=model))
            except Exception as exc:
                app.logger.exception("OpenAI chat failed: %s", exc)
                message = TextSendMessage(text="回覆失敗，晚點再試一次")

    if message:
        line_bot_api.reply_message(event.reply_token, message)

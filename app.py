import json
import os
import random as rd
import threading
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageMessage, ImageSendMessage, MessageEvent, TextMessage, TextSendMessage
from openai import BadRequestError

import github_api
import ggopenai


load_dotenv()

line_token = os.getenv("line_token") or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_secret = os.getenv("line_secret") or os.getenv("LINE_CHANNEL_SECRET")

app = Flask(__name__)
line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_secret)


def env_int(name, default):
    try:
        return max(0, int(os.getenv(name, default)))
    except ValueError:
        return default


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
BOYVFV_DIR = STATIC_DIR / "boyvfv"
LINE_UPLOAD_DIR = STATIC_DIR / "line_uploads"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
UPLOAD_COMMAND = os.getenv("LINE_IMAGE_UPLOAD_COMMAND", "上傳圖片")
UPLOAD_WINDOW_SECONDS = env_int("LINE_IMAGE_UPLOAD_WINDOW_SECONDS", 60)
APP_BASE_URL = "https://line-m800.onrender.com"
KEEP_ALIVE_ENABLED = True
KEEP_ALIVE_INTERVAL_SECONDS = 300
KEEP_ALIVE_TIMEOUT_SECONDS = 10
KEEP_ALIVE_PATH = "/callback"
KEEP_ALIVE_URL = f"{APP_BASE_URL}{KEEP_ALIVE_PATH}"
upload_sessions = {}
keep_alive_started = False


def public_base_url():
    return APP_BASE_URL.rstrip("/")


def static_url(path):
    return f"{public_base_url()}/static/{path.lstrip('/')}"


def image_message(static_path):
    image_url = static_url(static_path)
    return ImageSendMessage(
        original_content_url=image_url,
        preview_image_url=image_url,
    )


def random_static_image(directory, static_prefix):
    images = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if not images:
        return None

    selected = rd.choice(images)
    return f"{static_prefix}/{selected.name}"


def source_key(event):
    source = event.source
    return (
        getattr(source, "group_id", None)
        or getattr(source, "room_id", None)
        or getattr(source, "user_id", None)
        or "unknown"
    )


def begin_upload_session(event):
    upload_sessions[source_key(event)] = time.time() + UPLOAD_WINDOW_SECONDS


def consume_upload_session(event):
    key = source_key(event)
    expires_at = upload_sessions.get(key)
    if not expires_at:
        return False

    if time.time() > expires_at:
        upload_sessions.pop(key, None)
        return False

    upload_sessions.pop(key, None)
    return True


def save_line_image(message_id):
    LINE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.jpg"
    output_path = LINE_UPLOAD_DIR / file_name

    message_content = line_bot_api.get_message_content(message_id)
    with output_path.open("wb") as image_file:
        for chunk in message_content.iter_content():
            image_file.write(chunk)

    return f"line_uploads/{file_name}", output_path


def write_line_image_to_github(static_path, local_path):
    repo_path = f"static/{static_path}".replace("\\", "/")
    return github_api.upload_file(
        local_path=local_path,
        repo_path=repo_path,
        commit_message=f"Add LINE uploaded image {repo_path}",
    )


def keep_alive_url():
    return KEEP_ALIVE_URL


def keep_alive_loop():
    while True:
        time.sleep(KEEP_ALIVE_INTERVAL_SECONDS)
        target_url = keep_alive_url()
        if not target_url:
            app.logger.info("Keep-alive skipped: no public base URL configured")
            continue

        try:
            response = requests.get(target_url, timeout=KEEP_ALIVE_TIMEOUT_SECONDS)
            app.logger.info("Keep-alive ping %s -> %s", target_url, response.status_code)
        except requests.RequestException as exc:
            app.logger.warning("Keep-alive ping failed: %s", exc)


def start_keep_alive():
    global keep_alive_started

    if keep_alive_started or not KEEP_ALIVE_ENABLED or KEEP_ALIVE_INTERVAL_SECONDS <= 0:
        return

    if not keep_alive_url():
        app.logger.info("Keep-alive disabled: no public URL configured")
        return

    thread = threading.Thread(target=keep_alive_loop, name="render-keep-alive", daemon=True)
    thread.start()
    keep_alive_started = True


@app.route("/index", methods=["GET", "POST"])
def index():
    return "Hello World!!"


@app.route("/callback", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "OK"

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


@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    message = None

    if isinstance(event.message, ImageMessage):
        if consume_upload_session(event):
            try:
                static_path, local_path = save_line_image(event.message.id)
                if github_api.is_enabled():
                    write_line_image_to_github(static_path, local_path)
                    message = TextSendMessage(text="圖片上傳成功!")
                else:
                    message = TextSendMessage(text="圖片已儲存，尚未設定 GitHub 回寫")
            except github_api.GitHubUploadError as exc:
                app.logger.exception("GitHub image write-back failed: %s", exc)
                message = TextSendMessage(text="圖片已儲存，但 GitHub 回寫失敗")
            except github_api.GitHubConfigError as exc:
                app.logger.warning("GitHub image write-back skipped: %s", exc)
                message = TextSendMessage(text="圖片已儲存，GitHub 設定不完整")
            except Exception as exc:
                app.logger.exception("LINE image upload failed: %s", exc)
                message = TextSendMessage(text="圖片儲存失敗，請再試一次")
        else:
            return

        line_bot_api.reply_message(event.reply_token, message)
        return

    text = event.message.text.strip()

    if text == "銀河":
        static_path = random_static_image(BOYVFV_DIR, "boyvfv")
        if static_path:
            message = image_message(static_path)
        else:
            message = TextSendMessage(text="目前沒有銀河圖片")
    elif text == "抽":
        random_num = rd.randint(1, 134)
        message = image_message(f"roll/{random_num}_line.png")
    elif text == UPLOAD_COMMAND: # 上傳圖片
        begin_upload_session(event)
        message = TextSendMessage(text="請在 1 分鐘內傳送要儲存的圖片")
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
                message = TextSendMessage(text=ggopenai.cgpt(ask=ask))
            except Exception as exc:
                app.logger.exception("OpenAI chat failed: %s", exc)
                message = TextSendMessage(text="回覆失敗，晚點再試一次")

    if message:
        line_bot_api.reply_message(event.reply_token, message)


start_keep_alive()

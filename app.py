
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
from dotenv import load_dotenv

load_dotenv()
line_token = os.getenv('line_token')
line_secret = os.getenv('line_secret')

app = Flask(__name__)

# line_bot_api = LineBotApi(os.environ['line_token'])
# handler = WebhookHandler(os.environ['line_secret'])
line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == '銀河':
        message = TextSendMessage(text='大便')   
    if event.message.text == '妲黑':
        message = ImageSendMessage(
            original_content_url = r'https://raw.githubusercontent.com/lkevin861018/line/main/img/dahate.png?token=GHSAT0AAAAAACQ2QNNIAWTZHWSOU7ZRF6KMZQX2JAA',
            preview_image_url = r'https://raw.githubusercontent.com/lkevin861018/line/main/img/dahate.png?token=GHSAT0AAAAAACQ2QNNIAWTZHWSOU7ZRF6KMZQX2JAA'
            )
    # else:
    #     message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = False)
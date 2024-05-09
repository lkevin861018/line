
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import random as rd
from dotenv import load_dotenv
import dollar

load_dotenv()
line_token = os.getenv('line_token')
line_secret = os.getenv('line_secret')

app = Flask(__name__)

# line_bot_api = LineBotApi(os.environ['line_token'])
# handler = WebhookHandler(os.environ['line_secret'])
line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_secret)


@app.route('/index',methods = ['GET','POST'])
def index():
    return 'Hello World!!'

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
    url = 'https://linegg.onrender.com'
    if event.message.text == '銀河':
        message = TextSendMessage(text='大便')   
    elif event.message.text == '妲黑':
        message = ImageSendMessage(
            original_content_url = url+'/static/dahate.png',
            preview_image_url = url+'/static/dahate.png'
            )
    elif event.message.text == '凸':
        message = ImageSendMessage(
            original_content_url = url+'/static/fk.jpg',
            preview_image_url = url+'/static/fk.jpg'
            )
    elif event.message.text == '抽':
        random_num = rd.randint(1,60)
        message = ImageSendMessage(
            original_content_url = url+'/static/roll/%d.png'%random_num,
            preview_image_url = url+'/static/roll/%d.png'%random_num
            )
    
###########################################################################

    
    if event.message.text.find('!匯率') == 0 or event.message.text.find('！匯率') == 0:
        message = TextSendMessage(
            dollar.dollar(event.message.text.split(' ')[1])
        )

    if event.message.text.find('!股票') == 0 or event.message.text.find('！股票') == 0:
        message = TextSendMessage(
            dollar.stock(event.message.text.split(' ')[1])
        )    

###########################################################################

    if event.message.text == '!指令':
        message = TextSendMessage(text='銀河\n妲黑\n抽\n凸\n!匯率\n!股票\n')   

    if message:
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = False)
    
    

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os,re,dollar,translator,food,openai
import random as rd
from dotenv import load_dotenv

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

@handler.add(MessageEvent, message=(TextMessage,ImageMessage))
def handle_message(event):
    if isinstance(event.message,TextMessage):
        url = 'https://linegg.onrender.com'
        if event.message.text == '銀河':
            message = TextSendMessage(text='大便')   
        elif event.message.text == '妲黑':
            message = ImageSendMessage(
                original_content_url = url+'/static/dahate.png',
                preview_image_url = url+'/static/dahate.png'
                )
        elif event.message.text == '凸':
            random_num = rd.randint(1,2)
            message = ImageSendMessage(
                original_content_url = url+'/static/fk/fk%d.jpg'%random_num,
                preview_image_url = url+'/static/fk/fk%d.jpg'%random_num
                )
        elif event.message.text == '抽':
            random_num = rd.randint(1,63)
            message = ImageSendMessage(
                original_content_url = url+'/static/roll/%d.png'%random_num,
                preview_image_url = url+'/static/roll/%d.png'%random_num
                )
        elif event.message.text.find('消夜') >= 0 or event.message.text.find('宵夜') >= 0:
            message = TextSendMessage('麥當勞辣味雞塊')
        elif event.message.text == '開台啦':
            message = TextSendMessage('各位妲寶，妲妲開台啦 https://www.twitch.tv/dada_0124 !💕💕')
        elif event.message.text == '157':
            message = TextSendMessage('@恩💋妲 익은 Annie')
        
    ###########################################################################

        
        if event.message.text.find('!匯率') == 0 or event.message.text.find('！匯率') == 0:
            message = TextSendMessage(
                dollar.dollar(event.message.text.split(' ')[1])
            )

        if event.message.text.find('!股票') == 0 or event.message.text.find('！股票') == 0:
            message = TextSendMessage(
                dollar.stock(event.message.text.split(' ')[1])
            )    
        
        if event.message.text.find('#') == 0:
            txtb = re.findall('#{1}\S*\s{1}',event.message.text)[0]
            txt = event.message.text.split(txtb)[1]
            lang = event.message.text.split(' ')[0].split('#')[1]  
            message = TextSendMessage(
                translator.trans(txt = txt,lang = lang)
            ) 
        
        if event.message.text.find('$gpt') == 0:
            ask = event.message.text.split('$gpt\s')[1]
            message = TextSendMessage(
                openai.cgpt(ask = ask)
            ) 

        if event.message.text == '喝啥':
            message = TextSendMessage(food.what_to_drink())

    ###########################################################################

        if event.message.text == 'GG人':
            message = TextSendMessage(text='銀河\n妲黑\n抽\n凸\n!匯率\n!股票\n消夜 宵夜\n開台啦\n157\n')   

        if message:
            line_bot_api.reply_message(event.reply_token, message)

    ###########################################################################

    # if isinstance(event.message, ImageMessage):
    #     static_upload_path = os.path.join(os.path.dirname(__file__), 'static', 'upload')
    #     ext = 'jpg'
    #     message_content = line_bot_api.get_message_content(event.message.id)
    #     with tempfile.NamedTemporaryFile(dir=static_upload_path, prefix=ext + '-', delete=False) as tf:
    #         for chunk in message_content.iter_content():
    #             tf.write(chunk)
    #         tempfile_path = tf.name

    #     dist_path = tempfile_path + '.' + ext
    #     dist_name = os.path.basename(dist_path)
    #     os.rename(tempfile_path, dist_path)
    #     try:
    #         path = os.path.join('static', 'upload', dist_name)
    #         print(path)
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='上傳成功'))
    #     except:
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='上傳失敗'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = False)
    
    
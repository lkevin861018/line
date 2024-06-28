
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os,re,requests,time,threading,json
import dollar,food,ggopenai
from openai import BadRequestError
import random as rd
from dotenv import load_dotenv

load_dotenv()
line_token = os.getenv('line_token')
line_secret = os.getenv('line_secret')
group_id = os.getenv('group_id')
twitch_user_key = os.getenv('twitch_user_key')
twitch_client_id = os.getenv('twitch_client_id')

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
        events = json.loads(body).get('events', [])
        for event in events:
            if event['type'] == 'join' or 'message':
                group_id = event['source']['userId']
                print(f'Bot joined group: {group_id}')
    except Exception as e:
        print(e)



    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route('/da',methods = ['GET'])
def da():
    stream_status = request.args.get('stream_status')
    url = 'https://api.twitch.tv/helix/streams'
    params = {"user_login": "dada_0124"}
    # params = {"user_login": "rhythmy861018"}
    headers = {
        'Authorization': 'Bearer '+twitch_user_key,
        'Client-Id': twitch_client_id
    }

    
    response = requests.get(url, headers=headers, params=params)
    # print(stream_status)
    # print(response.json()['data']!=[])
    try:
        if response.json()['data']!=[] and stream_status == 'on':
            # line_bot_api.push_message(group_id, 
            #                         TextSendMessage(text='各位妲寶，妲妲開台啦 https://www.twitch.tv/dada_0124 !💕💕'))
            return 'off'
        elif response.json()['data']==[] and stream_status == 'off':
            # line_bot_api.push_message(group_id, 
            #                         TextSendMessage(text='各位妲寶，關台啦~回家洗洗睡!'))
            return 'on'
        else:
            return stream_status
    except:
        return stream_status
    
@app.route('/ggtalk',methods = ['GET'])
def ggtalk():
    try:
        talk = request.args.get('talk')
        line_bot_api.push_message(group_id,
                                TextSendMessage(text=talk))
        return 'push done' 
    except Error as e:
        return e


@handler.add(MessageEvent, message=(TextMessage,ImageMessage))
def handle_message(event):
    if isinstance(event.message,TextMessage):
        url = 'https://linegg.onrender.com'
        # if event.message.text == '銀河':
        #     message = TextSendMessage(text='大便')   
        # elif event.message.text == '妲黑':
        #     message = ImageSendMessage(
        #         original_content_url = url+'/static/dahate.png',
        #         preview_image_url = url+'/static/dahate.png'
        #         )
        # elif event.message.text == '凸':
        #     random_num = rd.randint(1,2)
        #     message = ImageSendMessage(
        #         original_content_url = url+'/static/fk/fk%d.jpg'%random_num,
        #         preview_image_url = url+'/static/fk/fk%d.jpg'%random_num
        #         )
        # elif event.message.text == '抽':
        #     random_num = rd.randint(1,63)
        #     message = ImageSendMessage(
        #         original_content_url = url+'/static/roll/%d.png'%random_num,
        #         preview_image_url = url+'/static/roll/%d.png'%random_num
        #         )
        # elif event.message.text.find('消夜') >= 0 or event.message.text.find('宵夜') >= 0:
        #     message = TextSendMessage('麥當勞辣味雞塊')
        # elif event.message.text == '157':
        #     message = TextSendMessage('@恩💋妲 익은 Annie')
        # elif event.message.text == '巧多多':
        #     message = TextSendMessage('忘記帶傘了')
        # elif event.message.text == '爛透了':
        #     message = TextSendMessage('就是在說你')
        # elif event.message.text == '呱呱':
        #     message = AudioSendMessage(
        #         original_content_url = url+'/static/audio/gua.ogg',
        #         duration=300
        #         )
        # elif event.message.text == '笑死':
        #     message = AudioSendMessage(
        #         original_content_url = url+'/static/audio/lmao.ogg',
        #         duration=5000
        #         )
        
    ###########################################################################

        
        if event.message.text.find('!匯率') == 0 or event.message.text.find('！匯率') == 0:
            message = TextSendMessage(
                dollar.dollar(event.message.text.split(' ')[1])
            )

        if event.message.text.find('!股票') == 0 or event.message.text.find('！股票') == 0:
            target = event.message.text.split(' ')[1]
            # rep = dollar.stock(target)
            rep = dollar.stock_ex(target)
            message = TextSendMessage(
                rep
            )
        
        # if event.message.text.find('#') == 0:
        #     txtb = re.findall('#{1}\S*\s{1}',event.message.text)[0]
        #     txt = event.message.text.split(txtb)[1]
        #     lang = event.message.text.split(' ')[0].split('#')[1]  
        #     message = TextSendMessage(
        #         translator.trans(txt = txt,lang = lang)
        #     ) 
        
       
        if event.message.text.find('@GG人畫圖') == 0:
            req = event.message.text.split('@GG人畫圖 ')[1]
            try:
                img_url = ggopenai.igpt(req = req)
                message = ImageSendMessage(
                original_content_url = img_url,
                preview_image_url = img_url
                )
            except BadRequestError:
                message = TextSendMessage('我是政確的狗汪汪!')
        elif event.message.text.find('@GG人4') == 0:
            ask = event.message.text.split('@GG人4 ')[1]
            message = TextSendMessage(
                ggopenai.cgpt(ask = ask,gen = "gpt-4o-2024-05-13")
            )
        elif event.message.text.find('@GG人') == 0:
            ask = event.message.text.split('@GG人 ')[1]
            message = TextSendMessage(
                ggopenai.cgpt(ask = ask,gen = "gpt-3.5-turbo-16k")
            )
            
        if event.message.text == '喝啥':
            message = TextSendMessage(food.what_to_drink())

    ###########################################################################

        # if event.message.text == 'GG人':
        #     message = TextSendMessage(text='銀河\n妲黑\n抽\n凸\n!匯率\n!股票\n消夜 宵夜\n157\n呱呱\n笑死\n')   

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

    try:
        print(event.message.text)
        if message:
            line_bot_api.reply_message(event.reply_token, message)
    except:
        pass

def periodic_task():
    stream_status = 'on'
    while True:
        da_url = 'https://linegg.onrender.com/da'
        params = {"stream_status": stream_status}
        stream_status = requests.get(da_url,params=params)
        # print(stream_status)
        time.sleep(600)
        # print(da_res.status_code)

# periodic_task()


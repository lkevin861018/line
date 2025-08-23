
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os,re,requests,time,threading,json
import dollar,food,ggopenai
from openai import BadRequestError
import random as rd
from dotenv import load_dotenv
from youtube import youtube_search

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
                group_id = event['source']['groupId']
                user_id = event['source']['userId']
                print(f'Bot joined group: {group_id},user: {user_id}')
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
        url = 'https://line-m800.onrender.com'
        if event.message.text == '銀河':
        #     message = TextSendMessage(text='是母狗')   
            message = ImageSendMessage(
                original_content_url = url+'/static/boyvfv_is_dog.jpg',
                preview_image_url = url+'/static/boyvfv_is_dog.jpg'
                )
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
        elif event.message.text == '抽':
            random_num = rd.randint(1,134)
            # if random_num == 50:
            #     message = ImageCarouselColumn(
            #     image_url = url+'/static/roll/%d_line.gif'%random_num,
            #     action=URITemplateAction(uri = url+'/static/roll/%d_line.gif'%random_num
            #     ))
            message = ImageSendMessage(
                original_content_url = url+'/static/roll/%d_line.png'%random_num,
                preview_image_url = url+'/static/roll/%d_line.png'%random_num
                )
        elif event.message.text.find('rolltest') == 0:
            test_num = event.message.text.split(' ')[1]
            # if test_num == 50:
            #     message = ImageCarouselColumn(
            #     image_url = url+'/static/roll/%d_line.gif'%random_num,
            #     preview_image_url = url+'/static/roll/%d_line.gif'%random_num
            #     )
            message = ImageSendMessage(
                original_content_url = url+'/static/roll/%s_line.png'%test_num,
                preview_image_url = url+'/static/roll/%s_line.png'%test_num
                )
        elif event.message.text == '班表':
            message = ImageSendMessage(
                original_content_url = url+'/static/schedule/25_sep.png',
                preview_image_url = url+'/static/schedule/25_sep.png'
                )
        
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
        elif event.message.text.find('@GG人') == 0:
            ask = event.message.text.split('@GG人 ')[1]
            message = TextSendMessage(
                ggopenai.cgpt(ask = ask,gen = "chatgpt-4o-latest")
                # ggopenai.cgpt(ask = ask,gen = "chatgpt-o3-mini")
            )

        if event.message.text.find('#yt') == 0:
            req = event.message.text
            query = re.split('#yt\d* ',req)[1]
            num = req.split(' ')[0].split('#yt')[1]
            if num == '':
                num = 1
            message = TextSendMessage(youtube_search(query,int(num)))
            


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
        da_url = 'https://line-m800.onrender.com/da'
        params = {"stream_status": stream_status}
        stream_status = requests.get(da_url,params=params)
        # print(stream_status)
        time.sleep(600)
        # print(da_res.status_code)

# periodic_task()


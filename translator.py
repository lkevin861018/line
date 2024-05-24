# from googletrans import Translator
# import json

# transcode = Translator()
# with open('language.json','r',encoding = 'utf8') as f:
#     lang_dict = json.load(fp = f)
# def trans(txt,lang):
#     try:
#         trans_txt = transcode.translate(txt,dest = lang_dict[lang]).text
#         return trans_txt
#     except:
#         return '換種語言試試'
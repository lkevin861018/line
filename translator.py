from googletrans import Translator
import json

trans = Translator()
with open('language.json','r',encoding = 'utf8') as f:
    lang_dict = json.load(fp = f)
def trans(txt,lang):
    try:
        trans_txt = trans.translate(txt,dest = lang_dict[lang]).text
        return trans_txt
    except:
        return '換種語言試試'
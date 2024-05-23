import requests
from bs4 import BeautifulSoup
import random as rd

url = f'https://zh.wikipedia.org/zh-tw/%E9%B8%A1%E5%B0%BE%E9%85%92%E5%88%97%E8%A1%A8'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
resp = requests.get(url, headers={
    'user-agent': user_agent
})

soup = BeautifulSoup(resp.text, 'html5lib')
divalc = soup.find_all('div', class_='div-col')

alc = ''
for d in divalc:
    alc = alc + d.text + '\n'
alc = alc.replace('\n',',').split(',')

def what_to_drink():
    while 1:
        drink = alc[rd.randint(1,len(alc)-1)]
        if drink != '':
            return drink.split('（')[0]
            break
            

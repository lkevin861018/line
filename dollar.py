import requests
from bs4 import BeautifulSoup

def dollar(cointype):
    url = f'https://www.google.com/search?q={cointype}換台幣'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    resp = requests.get(url, headers={
        'user-agent': user_agent
    })

    soup = BeautifulSoup(resp.text, 'html5lib')
    ele = soup.find('span', class_='DFlfde SwHCTb')

    if ele:
        return(f'目前 1 {cointype}為 {ele.text} 新台幣')
    else:
        return('目前沒有匯率')
    
def stock(no):
    url = f'https://www.google.com/search?q=台股{no}'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    resp = requests.get(url, headers={
        'user-agent': user_agent
    })

    soup = BeautifulSoup(resp.text, 'html5lib')
    ele = soup.find('div', id='main')
    price = ele.find('span',class_ = 'IsqQVc NprOob wT3VGc')

    if ele:
        return(f'目前 1 股 {no} 為 {price.text}')
    else:
        return('換一家試試')
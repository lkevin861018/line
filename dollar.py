import requests,json,time
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
    url1 = f'https://www.google.com/search?q={no}'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    resp = requests.get(url, headers={
        'user-agent': user_agent
    })
    resp1 = requests.get(url1, headers={
        'user-agent': user_agent
    })

    soup = BeautifulSoup(resp.text, 'html5lib')
    ele = soup.find('div', id='main')
    price = ele.find('span',class_ = 'IsqQVc NprOob wT3VGc')

    soup1 = BeautifulSoup(resp1.text, 'html5lib')
    ele1 = soup1.find('div', id='main')
    price1 = ele1.find('span',class_ = 'IsqQVc NprOob wT3VGc')

    if price:
        return f'目前 1 股 {no} 為 {price.text}'
    elif price1:
        return f'目前 1 股 {no} 為 {price1.text}'
    else:
        return '換一家試試'
    
def stock_ex(target):
    endpoint = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp'
    # Add 1000 seconds for prevent time inaccuracy
    timestamp = int(time.time() * 1000 + 1000000)
    query_url = '{}?_={}&ex_ch=tse_{}.tw'.format(endpoint, timestamp, target)
    response = requests.session().get(query_url)
    content = json.loads(response.text)
    try:
        stock_data =[
            content['msgArray'][0]['c'], # 股票代號
            content['msgArray'][0]['n'], # 股票名稱
            content['msgArray'][0]['t'], # 資料時間
            content['msgArray'][0]['z'], # 最近成交價
            content['msgArray'][0]['tv'], # 當盤成交量
            content['msgArray'][0]['v'], # 當日累計成交量
            content['msgArray'][0]['a'], # 最佳五檔賣出價格
            content['msgArray'][0]['f'], # 最價五檔賣出數量
            content['msgArray'][0]['b'], # 最佳五檔買入價格
            content['msgArray'][0]['g'] # 最佳五檔買入數量
        ]
        stock_data_txt = f'''股票代號:{stock_data[0]}\n股票名稱:{stock_data[1]}\n資料時間:{stock_data[2]}\n最近成交價:{stock_data[3]}\n當盤成交量:{stock_data[4]}\n當日累計成交量:{stock_data[5]}\n最佳五檔賣出價格:{stock_data[6]}\n最價五檔賣出數量:{stock_data[7]}\n最佳五檔買入價格:{stock_data[8]}\n最佳五檔買入數量:{stock_data[9]}\n'''
        return stock_data_txt
    except Exception as e:
        print(e)
        return '換一家試試'

if __name__ == '__main__':
    print(stock_ex(2330))
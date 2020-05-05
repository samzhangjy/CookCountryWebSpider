import requests, random
from utils.user_agent import getRandomUserAgent


def getRandomIP():
    # headers = {
    #     'User-Agent': str(getRandomUserAgent())
    # }
    # response = requests.get('http://http.tiqu.alicdns.com/getip3?num=250&type=3&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=2&sb=0&pb=4&mr=1&regions=&gm=4')
    ip = []
    with open('./ip.txt', 'r') as f:
        _ = f.read()
        ip = _.split('</br>')[:-1]
    return random.choice(ip)

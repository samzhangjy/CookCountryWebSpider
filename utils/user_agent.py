"""
User agent utils for the cookcountry clerk web spider
"""
import random

import requests
from bs4 import BeautifulSoup


def getUserAgents():
    """Get the user agents and store it to agents.txt file"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://developers.whatismybrowser.com/useragents/explore/'
    }
    for i in range(1, 11):
        source = requests.get(
            'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/mac-os-x/%d' % i, headers=headers)
        soup = BeautifulSoup(source.text, 'html.parser')
        for agent in soup.findAll('td', class_='useragent'):
            with open('macosx-agents.txt', 'a') as f:
                f.write(agent.find('a').text + '\n')


def getRandomUserAgent():
    """Get a random user-agent string from agents.txt
    :return: str, the random user agent string
    """
    agents = []
    with open('./agents.txt', 'r') as f:
        for line in f.readlines():
            agents.append(line.strip('\n'))
    return str(random.choice(agents))

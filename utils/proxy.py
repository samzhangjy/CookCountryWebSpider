"""
The proxy util to support the core
"""
import requests
import random
from utils.user_agent import getRandomUserAgent


def getRandomIP():
    """Get the random IP address"""
    # The code below is to get ip addresses dynamically based on the web spider,
    # but however it doesn't appeared to be working here anyway, so I commented
    # it out and just use the `ip.txt` stored in the root dir. But in that way,
    # I have to cmd-c & cmd-p everytime I changed the ip addresses, so this is just
    # temporory for now, until I thought up a better idea or a bug fix for this.
    # IMPORTANT :: THE CODE BELOW DOES NOT WORK, AND DO NOT REMOVE THE COMMENT UNLESS
    # YOU KNOW WHAT YOU ARE DOING
    ##########
    # Define the random user agent header
    # headers = {
    #     'User-Agent': str(getRandomUserAgent())
    # }
    # Get the source
    # response = requests.get('http://http.tiqu.alicdns.com/getip3?num=250&type=3&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=2&sb=0&pb=4&mr=1&regions=&gm=4')
    # There should be a splitting process here, as same as below
    ##########
    # Read from the file
    with open('./ip.txt', 'r') as f:
        # The actual file content
        _ = f.read()
        # Turn it into a list by splitting it using `</br>`
        # Note that [:-1] is for the last item in the list, otherwise it would be all blank
        # and have a possibility that it will throw out an error when it randomly chose
        # the last item in the list
        ip = _.split('</br>')[:-1]
    # Randomly return an ip address by using random.choice()
    return random.choice(ip)

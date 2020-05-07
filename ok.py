# -*- coding: utf-8 -*-
# @Author: Sam Zhang
# @Date:   2020-05-06 12:21:09
# @Last Modified by:   Sam Zhang
# @Last Modified time: 2020-05-06 18:25:07
import requests, multiprocessing
url = 'https://courtlink.lexisnexis.com/cookcounty/FindDock.aspx?NCase=1998D010000&SearchType=0&Database=4&case_no=&PLtype=1&sname=&CDate='
# url='http://www.baidu.com'

def test(t):
    try:
        a = requests.get(url=url, proxies=t, timeout=3)
        if a.content == bad:
            raise RuntimeError('Bad content')
        print(a.status_code)
    except:
        print('Junk:', t['http'])

with open('./ip.txt') as f:
    ip = f.read().split('</br>')[:-1]
bad = b'<html>\r\n\t<head>\r\n\t\t<title>Error</title>\r\n\t</head>\r\n\t<body>\r\n\t\tHost Error: There was an error processing your request. If you continue to \r\n\t\tencounter this error, please contact the site webmaster at: <a href="http://198.173.15.31/emailform/newmail.asp">\r\n\t\t\thttp://198.173.15.31/emailform/newmail.asp</a>, or telephone the internet \r\n\t\tcourt call help line at (312) 603-HELP (4357).\r\n\t</body>\r\n</html>\r\n'
if __name__ == '__main__':
    pool = multiprocessing.Pool()
    for x in ip:
        t = {
            'http': x
        }
        pool.apply_async(test, args=(t,))
    pool.close()
    pool.join()

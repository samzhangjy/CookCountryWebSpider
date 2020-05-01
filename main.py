"""
Main file for the Cook County docket
"""
import requests
from bs4 import BeautifulSoup
import datetime, random, time

import pymysql
import threading
from openpyxl import Workbook
import os, functools

# Open database connection
db = pymysql.connect('localhost', 'root', 'sam951951', 'CookCountry')

def getCaseDetails(case_year, division_code, case_id):
    """Get the case detail
    :param case_year: the year of the case
    :param division_code: the division code for the case
    :param case_id: the case id
    :return: when success, returns a dict with case number, plaintiff, defendant, 
    and filing date. If not, returns an empty dict.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11'
        }
        url = "http://httpbin.org/ip"
        proxy_host = "proxy.crawlera.com"
        proxy_port = "8010"
        proxy_auth = "15c8295558e5473a9fd81dd85ac83d22:" # Make sure to include ':' at the end
        proxies = {
            "https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
            "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}
        # print(proxies)
        # Grab the source code
        source = requests.get('http://courtlink.lexisnexis.com/cookcounty/FindDock.aspx?NCase=%s&SearchType=0&Database=4&case_no=&PLtype=1&sname=&CDate=' % str(case_year + division_code + case_id), headers=headers, 
            proxies=proxies, verify=False
        ).content
        # And initialize it with BeautifulSoup
        soup = BeautifulSoup(source, 'html.parser')
        # --- Case number ---
        # Simply find the number using bs4
        case_num = str(soup.find('span', id='lblBottom').text).replace('\n', '').strip()
        # --- End case number ---

        # --- Plaintiff ---
        # Find the base table list
        plaintiff_ = soup.find('div', id='objCaseDetails').findAll('table')[1].findAll('td')
        i = 0
        start = 0
        end = 0
        # Get the start point and the end point
        for _ in plaintiff_:
            if str(_.text).strip().replace('\n', '') == 'Plaintiff(s)':
                start = i
            i += 1
        plaintiff_ = plaintiff_[start+2:-1]  # Indice the list
        plaintiff = []  # <-- that's the real plaintiff list the function returns
        # Loop over all the items in list and check them
        for _ in plaintiff_:
            # If the current item is not nither in ('Attorney(s)', ''), put it into result
            if str(_.text).strip().replace('\n', '') not in ('Attorney(s)', ''):
                tmp = str(_.text).strip().replace('\n', '').split(' ')
                name = ''
                # Format the names
                for char in tmp:
                    name += ' ' + char.capitalize()
                plaintiff.append(name.strip())
            # Elsewise, if the item is empty, jump out the loop
            elif str(_.text).strip().replace('\n', '') == '':
                break
        # --- End plaintiff ---

        # --- Defendant ---
        # --- The earlier version ---
        # defendant_ = soup.find('div', id='objCaseDetails').findAll('table')[1].findAll('td')
        # i = 0
        # start = 0
        # # Get the start point only
        # for _ in defendant_:
        #     if str(_.text).strip().replace('\n', '') == 'Attorney(s)':
        #         start = i
        #     i += 1
        # defendant_ = defendant_[start+1:-1]
        # defendant = []
        # for _ in defendant_:
        #     # Same thing as plaintiff's
        #     if str(_.text).strip().replace('\n', '') != '':
        #         tmp = str(_.text).strip().replace('\n', '').split(' ')
        #         name = ''
        #         # Prettify the names as above
        #         for char in tmp:
        #             name += ' ' + char.capitalize()
        #         # Prevent some weird things that aren't what we wanted to go into our result
        #         if name.strip() != 'Pro Se':
        #             defendant.append(name.strip())
        #     else:
        #         # Check if the next 3 in the list are all empty <td></td>s
        #         # The flag to decied weather to keep or to leave
        #         flag = False
        #         for i in range(1, 4):
        #             try:
        #                 if str(defendant_[i].text).replace(' ', '') != '':
        #                     flag = True
        #             # If IndexError is raised, that means there's no more in the list
        #             except IndexError:
        #                 pass
        #         # Jump out of the loop if flag is False
        #         if not flag:
        #             break
        # --- End earlier version ---
        tbody = soup.findAll('tbody', limit=3)[1]
        trs = tbody.find_all('tr')
        trs = list(trs)
        defendant = []

        for _ in range(len(trs)):
            if trs[_].find_all('td')[0].text == 'Defendant(s)':
                tmp = str(trs[_+1].find_all('td')[0].text).strip().replace('\n', '').split(' ')
                name = ''
                # Prettify the names as above
                for char in tmp:
                    name += ' ' + char.capitalize()
                defendant.append(name.strip())
                if(len(trs[_+2:])) != 0:
                    for i in trs[_+2:]:
                        if i.find_all('td')[0].text not in (None, ''):
                            tmp = str(i.find_all('td')[0].text).strip().replace('\n', '').split(' ')
                            name = ''
                            # Prettify the names as above
                            for char in tmp:
                                name += ' ' + char.capitalize()
                            defendant.append(name.strip())
                
        # --- End defendant ---

        # --- Filing date ---
        # The date list, including year, month, and day
        filing_date_ = str(soup.find('div', id='objCaseDetails').find('table').find('tr').find('td').text).strip().replace('Filing Date: ', '').split('/')
        # Convert it into datetime.datetime format
        filing_date = datetime.datetime(year=int(filing_date_[2]), month=int(filing_date_[1]), day=int(filing_date_[0]))
        # --- End filing date ---

        # Gets the current url for better develop experience :)
        print('URL: ' + 'https://courtlink.lexisnexis.com/cookcounty/FindDock.aspx?NCase=%s&SearchType=0&Database=4&case_no=&PLtype=1&sname=&CDate=' % str(case_year + division_code + case_id))
        # Generate the result dict
        result = dict(case_num=case_num, plaintiff=plaintiff, defendant=defendant, filing_date=filing_date)
    except:
        # Returns an empty dict if an error accrued :-(
        return {}
    # Return the final result!
    return result


def storeToDatabase(result):
    """Store the given result to the database
    :param result: the result to store, usually generated by `getCaseDetails`
    :return: int, 0 for success, 1 for failed
    """
    try:
        # Prepare a cursor object using cursor() method
        cursor = db.cursor()
        # --- Format results ---
        # Case id
        caseId = result['case_num']
        # Plaintiffs
        plaintiffs = ','.join(result['plaintiff'])
        # Defendants
        defendants = ','.join(result['defendant'])
        # Filing date
        filing_date = '%d-%d-%d 00:00:00' % (result['filing_date'].year, result['filing_date'].month, result['filing_date'].day)
        # --- End format results ---

        # --- SQL ---
        sql = """INSERT INTO `Case` (caseId, defendants, plaintiffs, filing_date)
        VALUES ('%s', '%s', '%s', '%s');""" % (caseId, plaintiffs, defendants, filing_date)
        # Execute the SQL
        cursor.execute(sql)
        ### IMPORTANT: DON'T FORGET THIS LINE
        db.commit()
        # --- End SQL ---

        # Return 0 when success
        cursor.close()
        return 0
    except:
        # Otherwise, return 1 for error
        cursor.close()
        return 1


def storeToExcel(result):
    print('Storing data to excel...')
    # If the excel file exists, delete it
    if os.path.exists('./result.xlsx'):
        os.remove('./result.xlsx')
    # Create a new workbook
    wb = Workbook()
    # Select the current active sheet
    sheet = wb.active
    # Rename the sheet
    sheet.title = 'Result'
    # Insert the titles
    sheet['A1'] = 'ID'
    sheet['B1'] = 'Plaintiff'
    sheet['C1'] = 'Defandant(s)'
    sheet['D1'] = 'Filing Date'
    # Fill in the blanks
    i = 2
    for _ in result:
        # id
        id = _['case_num']
        print(id)
        sheet['A%d' % i] = id
        # Plaintiff
        plaintiff = ', '.join(_['plaintiff'])
        print(plaintiff)
        sheet['B%d' % i] = plaintiff
        # Defendants
        defendants = ', '.join(_['defendant'])
        print(defendants)
        sheet['C%d' % i] = defendants
        # Filing date
        filing_date = _['filing_date']
        print(filing_date)
        sheet['D%d' % i] = filing_date.strftime("%Y-%m-%d")
        i += 1
    
    wb.save('./result.xlsx')

# Tests with random ids and year
# persent = 0
# failed = 0
# total = 10
# for id in range(1, total + 1):
#     res = getCaseDetails(str(random.randint(1998, 2020)), 'D', str(id).zfill(6))
#     if res == {}:
#         total -= 1
#         continue
#     print(res)
#     if input('Correct? (y/n): ') == 'n':
#         failed += 1

# print('Correct persentage: {}%'.format(round((float(failed)/float(total)*100), 2)))

result = []
def spyder(case_year, division_code, case_id):
    # result = []
    _ = getCaseDetails(case_year, division_code, case_id)
    if _ != {}:
        result.append(_)
        print(_)
    else:
        print('Not found: %s%s%s' % (case_year, division_code, case_id))
    # result = [{'case_num': '1998D000001', 'plaintiff': ['Rojas Nancy'], 'defendant': ['Cochran Oscar'], 'filing_date': datetime.datetime(1998, 2, 1, 0, 0)}]
    # storeToExcel(result)
    print(result)

def getUserAgents():
    headers = {
            'User-Agent': 'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11'
    }
    source = requests.get('https://myip.ms/browse/comp_browseragents/Computer_Browser_Agents.html', headers=headers)
    soup = BeautifulSoup(source.text, 'html.parser')
    for agent in soup.findAll('td', class_='row_name'):
        with open('agents.txt', 'a') as f:
            f.write(agent.find('a').text + '\n')

def sortResult(x, y):
    if int(str(x['case_num'].split('D')[1]).lstrip('0') > str(y['case_num'].split('D')[1]).lstrip('0')):
        return 1
    else:
        return -1

def main():
    global result
    thread = []
    for i in range(1, 2001):
        thread.append(threading.Thread(target=spyder, args=('1998', 'D', str(i).zfill(6))))
    for t in thread:
        t.start()
    # for t in thread:
    #     t.join()
    result = sorted(result, key=functools.cmp_to_key(sortResult))
    storeToExcel(result)
        # time.sleep(3)
    # spyder('2020', 'D', '000001')
        
# input()
main()
# spyder('1998', 'D', '000001')

# -*- coding: utf-8 -*-
# @Author: Your name
# @Date:   2020-05-05 21:01:36
# @Last Modified by:   Your name
# @Last Modified time: 2020-05-05 21:44:14
"""
The core util for the web spider
"""
import datetime
from pprint import pprint as print

import requests
from bs4 import BeautifulSoup

from utils.proxy import getRandomIP
from utils.user_agent import getRandomUserAgent

results = []


def getCaseDetails(case_year, division_code, case_id):
    """Get the case detail
    :param case_year: the year of the case
    :param division_code: the division code for the case
    :param case_id: the case id
    :return: when success, returns a dict with case number, plaintiff, defendant, 
    filing date and case activity. If not, returns an empty dict.
    """
    try:
        # Define the random user agent header
        headers = {
            'User-Agent': str(getRandomUserAgent())
        }
        # Define the proxies from getRandomIP() function
        proxies = {
            "http": 'http://%s' % str(getRandomIP()),
        }
        # Grab the source code
        source = requests.get('http://courtlink.lexisnexis.com/cookcounty/FindDock.aspx?NCase=%s&SearchType=0&Database=4&case_no=&PLtype=1&sname=&CDate=' % str(case_year + division_code + case_id),
                              headers=headers, timeout=30, proxies=proxies
                              ).content
        # print(source)
        # And initialize it with BeautifulSoup
        soup = BeautifulSoup(source, 'html.parser')
        # --- Case number ---
        # Simply find the number using bs4
        case_num = str(soup.find('span', id='lblBottom').text).replace(
            '\n', '').strip()
        # --- End case number ---

        # --- Plaintiff ---
        # Find the base table list
        plaintiff_ = soup.find('div', id='objCaseDetails').findAll('table')[
            1].findAll('td')
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
                tmp = str(trs[_+1].find_all('td')
                          [0].text).strip().replace('\n', '').split(' ')
                name = ''
                # Prettify the names as above
                for char in tmp:
                    name += ' ' + char.capitalize()
                defendant.append(name.strip())
                if(len(trs[_+2:])) != 0:
                    for i in trs[_+2:]:
                        if i.find_all('td')[0].text not in (None, ''):
                            tmp = str(i.find_all('td')[0].text).strip().replace(
                                '\n', '').split(' ')
                            name = ''
                            # Prettify the names as above
                            for char in tmp:
                                name += ' ' + char.capitalize()
                            defendant.append(name.strip())

        # --- End defendant ---

        # --- Filing date ---
        # The date list, including year, month, and day
        filing_date_ = str(soup.find('div', id='objCaseDetails').find('table').find(
            'tr').find('td').text).strip().replace('Filing Date: ', '').split('/')
        # Convert it into datetime.datetime format
        filing_date = datetime.datetime(year=int(filing_date_[2]), month=int(
            filing_date_[1]), day=int(filing_date_[0]))
        # --- End filing date ---

        # --- Case Activity ---
        # Get the base table from source
        tables = soup.findAll('table')[2:]
        case_activity = []
        # Loop over every table
        for table in tables:
            # print(str(table.find('tr')))
            # Some condations when we are not going into the second loop
            if not len(table.findAll('tr')) < 2 and str(table.find('tr').text).isupper():
                activity = {}
                # Loop over the first two table row
                for tr in table.findAll('tr')[:2]:
                    # Original code
                    # for td in tr.findAll('td'):
                    #     try:
                    #         tdTable = td.findAll('table')[0].text.strip().strip('\n')
                    #     except:
                    #         tdTable = ''
                    #     print(td.text.strip('\n').replace(tdTable, ''))
                    # print(table)
                    # print(tr)
                    # for text in tr.findAll('td'):
                    #     if text is not None and str(text).strip():
                    #         print(text.text.strip())
                    # Bug fixed
                    if str(tr.text.replace('\n', '').strip()).isupper():
                        activity['title'] = str(
                            tr.text.replace('\n', '').strip())
                    else:
                        activity['detail'] = str(
                            tr.text.replace('\n', '').strip())
                case_activity.append(activity)
        # --- End case activity ---

        # Gets the current url for better develop experience :)
        # print('URL: ' + 'https://courtlink.lexisnexis.com/cookcounty/FindDock.aspx?NCase=%s&SearchType=0&Database=4&case_no=&PLtype=1&sname=&CDate=' %
        #      str(case_year + division_code + case_id))
        # Generate the result dict
        result = dict(case_num=case_num, plaintiff=plaintiff,
                      defendant=defendant, filing_date=filing_date, case_activity=case_activity)
    except:
        # Returns an empty dict if an error accrued :-(
        # raise
        return {}
    # Return the final result!
    return result


def spyder(case_year, division_code, case_id, store_to=None, print_out=False):
    """Get the case detail and store it
    :param case_year: str, the year of the given case, will be passed to `getCaseDetails`
    :param division_code: str, the division code of the given case,
    will be passed to `getCaseDetails`
    :param case_id: str, the id of the given case, will be passed to `getCaseDetails`
    :param store_to: function or method, will be run after gets the result. If None, then
    skip the store part. Defaults to None
    :param print_out: bool, weather to print the result out to the terminal or not.
    Defaults to False
    :return: int, 0 for success, 1 for failure
    """
    try:
        # Define the result
        _ = getCaseDetails(case_year, division_code, case_id)
        # If the result is not empty (or not found)
        if _ != {}:
            # Append it to the global result list
            results.append(_)
            if print_out:
                print(_)
        elif print_out:
            # Otherwise, it means not found / other reasons
            print('Not found: %s%s%s' % (case_year, division_code, case_id))
        # Check the store_to param
        if store_to is not None:
            # Store it
            store_to(result)
        # Success
        return 0
    except:
        # Failed
        raise
        return 1


def sortResult(x, y):
    """Sort the result by the given `x` and `y`
    :param x: the first param to compare
    :param y: the second param to compare
    :return: int, if x is greater than y, returns 1, otherwise, returns -1
    """
    if int(str(x['case_num'].split('D')[1]).lstrip('0') > str(y['case_num'].split('D')[1]).lstrip('0')):
        return 1
    else:
        return -1

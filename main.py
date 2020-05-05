# -*- coding: utf-8 -*-
# @Author: Your name
# @Date:   2020-05-05 21:02:15
# @Last Modified by:   Your name
# @Last Modified time: 2020-05-05 21:08:13
"""
     ██████╗ ██████╗  ██████╗ ██╗  ██╗ ██████╗ ██████╗ ██╗   ██╗███╗   ██╗████████╗██████╗ ██╗   ██╗    ███████╗██████╗ ██╗██████╗ ███████╗██████╗
    ██╔════╝██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ██╔════╝██╔══██╗██║██╔══██╗██╔════╝██╔══██╗
    ██║     ██║   ██║██║   ██║█████╔╝ ██║     ██║   ██║██║   ██║██╔██╗ ██║   ██║   ██████╔╝ ╚████╔╝     ███████╗██████╔╝██║██║  ██║█████╗  ██████╔╝
    ██║     ██║   ██║██║   ██║██╔═██╗ ██║     ██║   ██║██║   ██║██║╚██╗██║   ██║   ██╔══██╗  ╚██╔╝      ╚════██║██╔═══╝ ██║██║  ██║██╔══╝  ██╔══██╗
    ╚██████╗╚██████╔╝╚██████╔╝██║  ██╗╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║   ██║   ██║  ██║   ██║       ███████║██║     ██║██████╔╝███████╗██║  ██║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝       ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
    Main file for the Cook County docket web spider
"""
import threading
import time
from pprint import pprint as print

from tqdm import tqdm

from utils.core import spyder
from utils.storage import storeToDatabase
from utils.proxy import getRandomIP


def main(min_num=1, max_num=51):
    """Main function to start the program
    will gather the case information with case activity and case details from the website.
    Note that you will have to create a MySQL database with a table called Case and contains
    these four rows: id (int, primary key), case_id (varchar), plaintiffs (varchar), 
    defendants (varchar), filing_date (datetime) and case_activity (varchar, better be long)
    :param min_num: the min number to start with
    :param max_num: the max number to end with, notice that you have to plus one to the
    actual number you want 'cause its in the range() function
    """
    print('Getting case data...')
    start = time.time()
    # The threads list
    thread = []
    # Append all the threads
    for i in range(min_num, max_num):
        thread.append(threading.Thread(
            target=spyder, args=('1998', 'D', str(i).zfill(6), storeToDatabase)))
    # Start all threads
    for t in tqdm(thread):
        t.start()
    # Let the parent thread be idle before all its child threads are finished
    for t in tqdm(thread):
        t.join()
    end = time.time()
    total = end - start
    print('Total time cost: %d' % total)


# Run main function
main(max_num=20001)

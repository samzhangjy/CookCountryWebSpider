"""
Main file for the Cook County docket
"""
import threading
import time
from pprint import pprint as print

from tqdm import tqdm

from utils.core import spyder
from utils.storage import storeToDatabase


def main(min_num=1, max_num=51):
    """Main function to start the program
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
    for t in thread:
        t.join()
    end = time.time()
    total = end - start
    print('Total time cost: %d' % total)


# Run main function
main(max_num=501)

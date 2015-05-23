from crawler.fetcher import Fetcher
from tornado import gen
import tornado
import sys
import time
import logging

logging.disable(1000000)

COUNT = 10000

a = time.time()

@gen.coroutine
def task():
    global COUNT
    fetcher = Fetcher()
    t = yield fetcher.fetch('https://ezbuy.com')
    COUNT -= 1
    if not COUNT:
        print time.time() - a, 's'
        sys.exit(0)


def run():
    for i in range(COUNT):
        task()
run()
tornado.ioloop.IOLoop.instance().start()
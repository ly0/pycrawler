from task import BaseTask
from fetcher import Fetcher
from tornado import gen
import tornado
from consumer import Consumer
from rpc.rpc_json import Handler
from threading import Thread
import inspect


w = Fetcher()


#!/usr/bin/env python
# coding: utf-8

from tornado.web import Application, RequestHandler
from rpc import async, private

WEBSERVER_PORT = 10000
application = Application([
    (r'/', Handler),
], cookie_secret="COOKIESECRETS")


def auth(username, password):
    return True


def authenticated(auth_func):

    def add_auth(func):
        func._need_authenticated = auth_func
        return func

    return add_auth

def testauth(username, password):
    if username == 'test' and password == 'test2':
        return True

    return False


class Carters(BaseTask):


    @authenticated(testauth)
    @async
    def category(self, store_id, slug):
        self.rpc_handler.result('Start %s' % slug)
        self.slug = slug
        self.store_id = store_id
        self.crawl_category()
        #return {'msg': '%s has been lauched.' % slug}

    @gen.coroutine
    @private
    def crawl_category(self):
        fetcher = Fetcher()
        from pyquery import PyQuery as PQ
        import json

        kk = yield fetcher.fetch("http://www.carters.com/%s?startRow=0&sz=all" % self.slug)
        page = kk.body
        pq = PQ(page)
        data = []
        products = pq('li.grid-tile')
        for product in products:
            foo = PQ(product)
            origin_price = foo('.product-standard-price').text().replace('MSRP:', '').replace('$', '').strip()
            if not origin_price:
                continue
            data.append({'image': foo('img').attr('src'),
                         'link': foo('.name-link').attr('href'),
                         'title': foo('.name-link').text(),
                         'original_price': origin_price,
                         'sales_price':foo('.product-sales-price').text().replace('$', '').strip()
                         })



        q = yield fetcher.fetch('http://127.0.0.1:8000/ezlookup/deal/?key=998998998', method="POST", data={
            'website': 'carters',
            'currency': 'USD',
            'country': 'USA',
            'store_id': self.store_id,
            'data': json.dumps(data)
        })


from pyquery import PyQuery as PQ
import json
import re

class SixPM(BaseTask):

    @authenticated(auth)
    @async
    def category(self, store_id, slug):
        self.rpc_handler.result('Start %s' % slug)
        self.slug = slug
        self.store_id = store_id
        self.get_category_page()

    @gen.coroutine
    def get_category_page(self):
        fetcher = Fetcher()


        ret = yield fetcher.fetch('http://www.6pm.com/%s' % self.slug)
        body = PQ(ret.body)
        foo = body('.last a')[0].get('href')
        max_page = int(re.findall('-page(\d+)', foo)[0])
        for i in range(max_page):
            self._crawl_category_page(i)

    @gen.coroutine
    def _crawl_category_page(self, page):
        fetcher = Fetcher()
        url = 'http://www.6pm.com/{slug}-page{page}/.zso?p={page}'.format(slug=self.slug, page=page)
        ret = yield fetcher.fetch(url)
        body = PQ(ret.body)
        products = body('.product')
        print products



@gen.coroutine
def run():
    consumer = Consumer('amqp://guest:guest@localhost:5672/%2F', queue='text', routing_key='example.text')
    consumer.run()
    print 'runed'
#    kk = yield w.fetch("http://www.abercrombie.cn/on/demandware.store/Sites-abercrombie_cn-Site/en_CN/Product-Variation?pid=anf-87741&dwvar_anf-87741_4MPrmry=4080&dwvar_anf-87741_color=01&Quantity=1&format=ajax&_=1431591378963")
    kk = yield w.fetch('http://127.0.0.1:8000')
    kk = yield w.fetch('http://127.0.0.1:8000', method="POST", headers={'User-Agent':'FUCK'})
    Handler.carters = Carters()
    Handler.sixpm = SixPM()
    application.listen(WEBSERVER_PORT)
    #runrpc()

run()

#get("http://www.google.com", callback=callback_test)
tornado.ioloop.IOLoop.instance().start()
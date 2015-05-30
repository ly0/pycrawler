from task import BaseTask
from fetcher import Fetcher
from tornado import gen
import tornado
from consumer import Consumer
from rpc.rpc_json import Handler
from threading import Thread
import inspect
from pyquery import PyQuery as PQ
import json
import re

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
    if username == 'ezbuy' and password == 'ezbuy88881111':
        return True

    return False


def parse_url(url):
    import urlparse
    parser = urlparse.urlparse(url)
    parsed_url = 'http://{netloc}{path}'.format(netloc=parser.netloc, path=parser.path)

    ids = re.findall('[?&](id=[^&]+)', url)
    if ids:
        parsed_url = '%s?%s' % (parsed_url, '&'.join(ids))

    return parsed_url

class Carters(BaseTask):


    @authenticated(testauth)
    @async
    def category(self, slug, store_id, **kwargs):
        self.rpc_handler.result('Start %s' % slug)
        self.slug = slug
        self.store_id = store_id
        self.crawl_category()
        self._extra_kwargs = kwargs
        #return {'msg': '%s has been lauched.' % slug}

    @gen.coroutine
    @private
    def crawl_category(self):
        fetcher = Fetcher()
        kk = yield fetcher.fetch("http://www.carters.com/%s?startRow=0&sz=all" % self.slug)
        page = kk.body

        self._process(page)


    def _process(self, page):
        pq = PQ(page)
        data = []
        products = pq('li.grid-tile')
        for product in products:
            foo = PQ(product)
            #origin_price = foo('.product-standard-price').text().replace('MSRP:', '').replace('$', '').strip()
            origin_price = re.findall('[\d\.]+', foo('.product-standard-price').text())
            sales_price = re.findall('[\d\.]+', foo('.product-sales-price').text())
            if not origin_price or not sales_price:
                continue
            data.append({'image': foo('img').attr('src'),
                         'link': parse_url(foo('.name-link').attr('href')),
                         'title': foo('.name-link').text(),
                         'original_price': origin_price[0],
                         'sales_price': sales_price[0]
                         })


        data = {
            'website': 'carters',
            'currency': 'USD',
            'country': 'USA',
            'store_id': self.store_id,
            'data': json.dumps(data)
        }
        data.update(self._extra_kwargs)

        self._save(data)

    @gen.coroutine
    def _save(self, data):
        fetcher = Fetcher()
        q = yield fetcher.fetch('http://127.0.0.1:8000/ezlookup/deal/?key=998998998', method="POST", data=data)

    @private
    def crawl_url(self, url, store_id, **kwargs):
        pass



class SixPM(BaseTask):

    @authenticated(auth)
    @async
    def category(self, store_id, slug):
        self.rpc_handler.result('Start %s' % slug)
        self.slug = slug
        self.store_id = store_id
        self._get_category_page()

    @gen.coroutine
    def _get_category_page(self):
        fetcher = Fetcher()
        ret = yield fetcher.fetch('http://www.6pm.com/%s' % self.slug)
        body = PQ(ret.body)
        foo = body('.last a')[0].get('href')
        max_page = int(re.findall('-page(\d+)', foo)[0])
        for i in range(max_page):
            self._crawl_category_page(i)

    def _crawl_category_page(self, page):
        url = 'http://www.6pm.com/{slug}-page{page}/.zso?p={page}'.format(slug=self.slug, page=page)
        self.crawl_url(url)

    def crawl_url(self, url, store_id, **kwargs):
        self.rpc_handler.result('Done')
        self.store_id = store_id
        self._crawl_url(url)
        self._extra_kwargs = kwargs

    @gen.coroutine
    def _crawl_url(self, url):
        fetcher = Fetcher()
        ret = yield fetcher.fetch(url)
        body = PQ(ret.body)
        products = body('a.product')

        data = []
        for product in products:
            foo = PQ(product)
            origin_price = re.findall('\$([\d\.]+)', foo('.discount').text())
            if origin_price:
                origin_price = origin_price[0]
            sales_price = foo('.price-6pm').text().replace('$', '').strip()

            if not origin_price and not sales_price:
                continue
            title = '[%s] %s' % (foo('.brandName').text(), foo('.productName').text())

            data.append({'image': foo('.productImg').attr('src'),
                         'link': parse_url('http://www.6pm.com' + foo('a').attr('href')),
                         'title': title,
                         'original_price': origin_price or sales_price,
                         'sales_price': sales_price
                         })

        data = {
            'website': '6pm',
            'currency': 'USD',
            'country': 'USA',
            'store_id': self.store_id,
            'data': json.dumps(data)
        }
        data.update(self._extra_kwargs)

        q = yield fetcher.fetch('http://127.0.0.1:8000/ezlookup/deal/?key=998998998', method="POST", data=data)




@gen.coroutine
def run():
    consumer = Consumer('amqp://guest:guest@127.0.0.1:5672/%2F', queue='text', routing_key='example.text')
    consumer.run()
    print 'runed'
#    kk = yield w.fetch("http://www.abercrombie.cn/on/demandware.store/Sites-abercrombie_cn-Site/en_CN/Product-Variation?pid=anf-87741&dwvar_anf-87741_4MPrmry=4080&dwvar_anf-87741_color=01&Quantity=1&format=ajax&_=1431591378963")
    kk = yield w.fetch('http://www.abercrombie.cn/en_CN/mens-shorts-twill-classic-fit/aandf-classic-fit-shorts/anf-87743.html?dwvar_anf-87743_color=01#ict=ICT%3ASUM15%3AM%3AHT%3A1%3AT%3ASEA%3AShorts&start=1')

    #kk = yield w.fetch('http://127.0.0.1:8000', method="POST", headers={'User-Agent':'FUCK'})
    Handler.carters = Carters()
    Handler.sixpm = SixPM()
    application.listen(WEBSERVER_PORT)
    #runrpc()

run()

#get("http://www.google.com", callback=callback_test)
tornado.ioloop.IOLoop.instance().start()
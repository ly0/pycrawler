from crawler.task import BaseTask
from crawler.decorators.rpc.auth import authenticated
from crawler.rpc.tornadorpc import async, private
from crawler.fetcher import Fetcher
from crawler.decorators.tornado import gen
from settings.functions import testauth
import re
import json
import urlparse
from pyquery import PyQuery as PQ

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
        kk = yield self.fetch("http://www.carters.com/%s?startRow=0&sz=all" % self.slug, next=self._process)


    def _process(self, page):
        data = []
        products = page('li.grid-tile')
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

        self.save(data)

    @gen.coroutine
    def save(self, data):
        fetcher = Fetcher()
        q = yield fetcher.fetch('http://127.0.0.1:8000/ezlookup/deal/?key=998998998', method="POST", data=data)

    @private
    def crawl_url(self, url, store_id, **kwargs):
        # URL preprocess
        fetcher = Fetcher()
        kk = yield fetcher.fetch(url)
        page = kk.body

        self._process(page)
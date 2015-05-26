from crawler.task import BaseTask
from crawler.decorators.rpc.auth import authenticated
from crawler.rpc.tornadorpc import async
from crawler.fetcher import Fetcher
from crawler.decorators.tornado import gen
from settings.functions import testauth as auth

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

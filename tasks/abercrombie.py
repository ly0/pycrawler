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

class Abercrombie(BaseTask):

    @authenticated(testauth)
    @async
    def update_product(self, url, **kwargs):
        real_url = parse_url(url)
        self.rpc_handler.result(True)
        self._update_product(real_url, **kwargs)

    @gen.coroutine
    @private
    def _update_product(self, url, **kwargs):
        ret = yield self._fetcher.fetch(url)
        body = PQ(ret.body)

        data = {
            'website': 'abercrombie',
            'currency': 'USD',
            'title': body('title').text().split('|')[0].strip(),
            'thumb': body('.primary-image').attr('src'),
            'price': re.findall('[\d\.]+', body('.price-sales').text())[0],
            'origin_price': re.findall('[\d\.]+', body('.price-sales').text())[0]
            }

        data.update(kwargs)
        q = yield self._fetcher.fetch('http://127.0.0.1:8000/ezlookup/product-update/?key=998998998', method="POST", data=data)
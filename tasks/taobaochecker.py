from crawler.task import BaseTask
from crawler.decorators.rpc.auth import authenticated
from crawler.rpc.tornadorpc import async
from crawler.fetcher import Fetcher
from crawler.decorators.tornado import gen
from settings.functions import testauth as auth

import re
import json


class TaobaoChecker(BaseTask):

    @authenticated(auth)
    @async
    def check(self, ids):
        if not isinstance(ids, list):
            self.rpc_handler.result('ids must be list')
            return
        self.rpc_handler.result('Done')
        print 'holy shit'
        self._check(ids)

    @gen.coroutine
    def _check(self, ids):
        BASE_URL = 'http://hws.m.taobao.com/cache/wdetail/5.0/?id={id}'
        cookies = ''
        for pid in ids:
            self.fetch(BASE_URL.format(id=pid), args=(pid,), data_type='json', next=self._process, headers={'Cookie': cookies})


    def _process(self, data, pid):
        try:
            price_data = json.loads(data['data']['apiStack'][0]['value'])
            if 'errorMessage' in price_data['data']['itemControl']['unitControl']:
                self.save(pid)
        except:
            self.save(pid)

    def save(self, pid):
        # this product is not available anymore
        super(TaobaoChecker, self).save({"product_id": pid})
        #print pid

# coding=utf-8
from crawler.task import BaseTask
from crawler.decorators.rpc.auth import authenticated
from crawler.rpc.tornadorpc import async
from crawler.decorators.tornado import gen
from settings.functions import testauth as auth
from pyquery import PyQuery as PQ
import re


class Carrefour(BaseTask):

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
        BASE_URL = 'http://www.carrefour.cn/product/2500{id}'
        for pid in ids:
            self.fetch(BASE_URL.format(id=pid), args=(pid,), next=self._process)


    def _process(self, data, pid):
        if '/product/' not in data._resp.effective_url:
            return
        props = dict([PQ(i).text().split(u'：') for i in data('.detail-tab-pro-info li')])
        print props

        try:
            categories = [{re.findall('\d+', PQ(i).attr('href'))[0]: PQ(i).text()} for i in data('.breadcrumbs a')[1:]]
        except:
            categories = []

        ret = {
            'title': data('#sec_productTitle').text(),
            'category_id': data('#hid_categoryId').attr('value'),
            'category_tree': categories,
            'keywords': data('meta[name=Keywords]').attr('content').split(u'，'),
            'property': props,
            'image': 'http://www.carrefour.cn%s' % data('li.select img').attr('bimg')
        }

        # Brand
        if u'品牌' in props:
            brand = props[u'品牌']

            left_columns = data('.middle-left01')
            target = None
            for column in left_columns:
                if u'相关品牌' == PQ(column)('p.left-title').text():
                    target = PQ(column)

            if target:
                foo = PQ(target('a')[0])
                url = foo.attr('href')
                brand_id = re.findall('b=(\d+)', url)[0]
                brand_text = foo.text()
                if brand_text == brand:
                    ret['brand'] = {
                        'brand_name': brand,
                        'brand_id': brand_id
                    }

        self.save(ret)
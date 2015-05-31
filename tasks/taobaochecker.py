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
        cookies = 'thw=cn; cna=tfK8Db+Be2cCAbStQEsS6j+9; wud=wud; tma=6906807.30423219.1430129109730.1430129109730.1430722880532.2; tmd=2.6906807.30423219.1430129109730.; lzstat_uv=26785475772932934127|3492151@1259840@3350652@3385238; lzstat_ss=1327143624_0_1429786723_3492151|2365255229_0_1429786729_1259840|1174962433_0_1429786744_3350652|2893976667_0_1430851434_3385238; _w_app_lg=18; ali_ab=180.173.65.84.1430996556504.2; whl=-1%260%260%260; WAPFDFDTGFG=%2B4cMKKP%2B8PI%2BMLrMGeCpeMPPeGxnFOKWPNf4j4t8%2BDGH0rUZx%2F%2BNixVAUZNihtGYuyo3; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; supportWebp=false; ck1=; v=0; linezing_session=GHV9HSkfBtqYaYkXyzWR1ofu_1432356192885qtdG_22; _m_h5_tk=5918a129287d429765772534a3eaf25c_1432609177287; _m_h5_tk_enc=18bcede50ce4d3a92100bf085b4fe846; uc3=nk2=odNz7hzuWQYWqJCo7FfUEmo%3D&id2=UUwRmDo6zEvsUA%3D%3D&vt3=F8dAT%2BM5IsABVWtbg%2BA%3D&lg2=V32FPkk%2Fw0dUvg%3D%3D; existShop=MTQzMjY5NjA4NA%3D%3D; unt=%E9%A9%AC%E8%8A%B8%E6%88%91%E8%B5%90%E4%BD%A0%E5%A7%A8%E5%A6%88poi%26center; lgc=%5Cu9A6C%5Cu82B8%5Cu6211%5Cu8D50%5Cu4F60%5Cu59E8%5Cu5988poi; tracknick=%5Cu9A6C%5Cu82B8%5Cu6211%5Cu8D50%5Cu4F60%5Cu59E8%5Cu5988poi; sg=i65; _cc_=VT5L2FSpdA%3D%3D; tg=0; _l_g_=Ug%3D%3D; mt=ci=95_1&cyk=0_1; cookie2=1ce8c31d2f130769f809f4792c809356; cookie1=B0b8GxLN4sdZR%2Bjqp58nwJMXUXfp8fjkCv7LqxCiY5s%3D; unb=2412300166; t=1a437fe2c85ce31ed18074f12b61ba8c; _nk_=%5Cu9A6C%5Cu82B8%5Cu6211%5Cu8D50%5Cu4F60%5Cu59E8%5Cu5988poi; cookie17=UUwRmDo6zEvsUA%3D%3D; _tb_token_=BzmkK6lE959f; uc1=lltime=1432636397&cookie14=UoW0EPov35lS%2FQ%3D%3D&existShop=true&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&cookie21=VT5L2FSpccLuJBreKQgf&tag=7&cookie15=W5iHLLyFOGW7aA%3D%3D&pas=0; l=AltbZomINbCyVaOWPcjy7wSza7HFMG8y; ubn=p; ucn=center; isg=FFA1A315963B10D4A6739F7E08AE06A9'
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
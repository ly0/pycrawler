from tornado import gen
from fetcher import Fetcher
import simplejson as json
from pyquery import PyQuery as PQ
import tornado

class Response(dict):
    def __init__(self, resp, data_type):
        self._resp = resp
        self._type = data_type
        if data_type == 'json':
            self.update(json.loads(resp.body))
        elif data_type == 'html':
            self.body = resp.body
        self.code = resp.code

    def __call__(self, csspath):
        if self._type == 'html':
            return PQ(self.body)(csspath)
        else:
            return self

    def __repr__(self):
        if self._type == 'html':
            return '<HTTP Response %s: %s>' % (self.code, self._resp.effective_url)
        else:
            return super(Response, self).__repr__()


class BaseTask(object):
    def __init__(self):
        self.fetcher = Fetcher()
        self._enter()

    def _enter(self):
        self.on_start()
        self._exit()

    def on_start(self):
        raise NotImplemented

    def _exit(self):
        pass

    @gen.coroutine
    def fetch(self, url, next, data_type="html", **kwargs):
        '''
        :param url: URL will be fetched
        :param callback: callback function
        :param data_type: html/json/xml
        :return:
        '''
        ret = yield self.fetcher.fetch(url, **kwargs)
        next(Response(ret, data_type))

    @gen.coroutine
    def save(self, ):


class Taobao(BaseTask):
    def on_start(self):
        # self.fetch('http://amazon.cn', next=self.test)
        # self.fetch('http://www.baidu.com', next=self.test)
        # self.fetch('http://www.abercrombie.cn/on/demandware.store/Sites-abercrombie_cn-Site/en_CN/Product-Variation?pid=anf-87741&dwvar_anf-87741_4MPrmry=4080&dwvar_anf-87741_color=01&Quantity=1&format=ajax&_=1431591378963', next=self.test)
        self.fetch('http://hws.m.taobao.com/cache/wdetail/5.0/?id=16452516831', data_type="json", next=self.test)
    def test(self, resp):
        print resp


t = Taobao()
tornado.ioloop.IOLoop.instance().start()
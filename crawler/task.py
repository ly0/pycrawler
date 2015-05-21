from tornado import gen
from fetcher import Fetcher
from response import Response

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
    def save(self, data):
        '''save to mongodb, overlay it when you want to change behavior of save
        :param data:
        :return:
        '''
        raise NotImplemented()
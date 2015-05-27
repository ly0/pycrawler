from tornado import gen
from fetcher import Fetcher
from response import Response
from .db import mongo_client
import logging
import log


class TaskMeta(type):
    def __init__(cls, name, bases, attrs):
        # init db connection
        cls._db = mongo_client[name]
        cls.logger = logging.getLogger('Task:%s' % name)

class BaseTask(object):
    __metaclass__ = TaskMeta

    def __init__(self):
        self.fetcher = Fetcher()

    def on_start(self):
        raise NotImplemented

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
        if not isinstance(data, dict):
            raise TypeError('data must be instance of dict')

        result = yield self._db.insert(data)
        self.logger.info("Saved: " + str(result))
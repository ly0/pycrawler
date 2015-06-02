from tornado import gen
from fetcher import Fetcher
from response import Response
from .db import mongo_client
import logging
import datetime
import log


class TaskMeta(type):
    def __init__(cls, name, bases, attrs):
        # init db connection
        cls._db = mongo_client[name]
        cls._logger = logging.getLogger('Task:%s' % name)

class BaseTask(object):
    __metaclass__ = TaskMeta

    def __init__(self, max_connection=998):
        self._fetcher = Fetcher()

    def on_start(self):
        raise NotImplemented

    @gen.coroutine
    def fetch(self, url, next=None, args=(), data_type="html",  **kwargs):
        '''
        :param url: URL will be fetched
        :param next: callback function
        :param args: arguments passed to callback function after data, if callback function is not specified,
                     args will be ignored.
        :param data_type: html/json/xml
        :return:
        '''
        ret = yield self._fetcher.fetch(url, **kwargs)

        if next:
            # Use callback
            next(Response(ret, data_type), *args) # Wrapp in Response Object
        else:
            # Use yield
            raise gen.Return(Response(ret, data_type))


    @gen.coroutine
    def save(self, data):
        '''save to mongodb, overlay it when you want to change behavior of save
        :param data:
        :return:
        '''
        if not isinstance(data, dict):
            raise TypeError('data must be instance of dict')

        # add time stamp
        data.update({'_timestamp': datetime.datetime.utcnow()})

        result = yield self._db.insert(data)
        self._logger.info("Saved: " + str(result))

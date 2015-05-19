from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop


@gen.coroutine
def test():
    client = AsyncHTTPClient()
    ret = yield client.fetch('http://127.0.0.1:8000')
    raise gen.Return(ret.body)


@gen.coroutine
def run():
    print 'run invoked'
    ret = yield test()
    print 'Done'

run()
run()
run()
IOLoop.instance().start()
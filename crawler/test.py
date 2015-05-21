from fetcher import Fetcher
from tornado import gen
import tornado
from consumer import Consumer
from rpc.rpc_json import Handler
from threading import Thread

w = Fetcher()


#!/usr/bin/env python
# coding: utf-8

from tornado.web import Application, RequestHandler

WEBSERVER_PORT = 10000
application = Application([
    (r'/', Handler),
], cookie_secret="COOKIESECRETS")


def auth(username, password):
    return True

from decorators.basicauth import authenticated

def authenticated(auth_func):

    def add_auth(func):
        func._need_authenticated = auth_func
        return func

    return add_auth

def testauth(username, password):
    if username == 'test' and password == 'test2':
        return True

    return False


class Carters(object):

    @authenticated(testauth)
    def category(self, slug):
        return {'msg': '%s has been lauched.' % slug}


@gen.coroutine
def run():
    consumer = Consumer('amqp://guest:guest@localhost:5672/%2F', queue='text', routing_key='example.text')
    consumer.run()
    print 'runed'
#    kk = yield w.fetch("http://www.abercrombie.cn/on/demandware.store/Sites-abercrombie_cn-Site/en_CN/Product-Variation?pid=anf-87741&dwvar_anf-87741_4MPrmry=4080&dwvar_anf-87741_color=01&Quantity=1&format=ajax&_=1431591378963")
    kk = yield w.fetch('http://127.0.0.1:8000')
    kk = yield w.fetch('http://127.0.0.1:8000', method="POST", headers={'User-Agent':'FUCK'})
    Handler.carters = Carters()
    application.listen(WEBSERVER_PORT)
    #runrpc()

run()

#get("http://www.google.com", callback=callback_test)
tornado.ioloop.IOLoop.instance().start()
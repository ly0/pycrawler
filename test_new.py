# coding=utf-8
import tornado
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado import gen
from pyquery import PyQuery as PQ
import cookies
import requests


AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

import Cookie

def cookie_to_dict(cookie):
    """Convert a string cookie into a dict"""
    cookie_dict = dict()
    C = Cookie.SimpleCookie()
    C.load(cookie)
    print cookie
    print '*', C
    for morsel in C.values():
        cookie_dict[morsel.key] = morsel.value
    return cookie_dict

def callback_test(resp):
    global w
    print cookies.get_cookie(resp.request, resp)
    print type(cookies.get_cookie(resp.request, resp))
    w.fetch("http://www.google.com", callback_test)


class Fetcher(AsyncHTTPClient):
    def __init__(self, *args, **kwargs):
        super(Fetcher, self).__init__(*args, **kwargs)

        self._cookies = ''
        self.session = HTTPRequest('', follow_redirects=False)
        self.cookiejar = requests.cookies.RequestsCookieJar()


    def pre_request(self, req):
        # set cookies
        cookie = cookies.dict_to_cookie(self.cookiejar)
        req.headers.update({'Cookie': cookie})
        print cookie
        req.headers.update({'User-Agent': 'Mozilla/5.0'})

    def post_request(self, req, resp):
        # save cookies
        cookies.make_cookiejar(self.cookiejar, req, resp)

    @gen.coroutine
    def fetch(self, url, **kwargs):
        http_client = AsyncHTTPClient()
        self.session.url = url

        for k, v in kwargs.items():
            setattr(self.session, k, v)

        while True:
            self.pre_request(self.session)

            try:
                #response = yield http_client.fetch(self.session, **kwargs)
                response = yield super(Fetcher, self).fetch(self.session, **kwargs)
                print 'DONE'
                break
            except HTTPError as httperr:
                print 'ERR'
                if httperr.code > 300 and httperr.code < 400:
                    self.post_request(self.session, httperr.response)
                    self.session.url = httperr.response.effective_url
                    print httperr.response.effective_url
        print 'DONE'
        self.post_request(self.session, response)

        raise gen.Return(response)




w = Fetcher()

@gen.coroutine
def run():
    print 'runed'
    kk = yield w.fetch("http://www.abercrombie.cn/on/demandware.store/Sites-abercrombie_cn-Site/en_CN/Product-Variation?pid=anf-87741&dwvar_anf-87741_4MPrmry=4080&dwvar_anf-87741_color=01&Quantity=1&format=ajax&_=1431591378963")
    print kk.body
run()

#get("http://www.google.com", callback=callback_test)
tornado.ioloop.IOLoop.instance().start()
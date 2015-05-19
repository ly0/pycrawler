# coding=utf-8
import copy
import logging
import urllib
import tornado
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado import gen
import cookies
import requests


logger = logging.getLogger('fetcher')

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

def callback_test(resp):
    global w
    print cookies.get_cookie(resp.request, resp)
    print type(cookies.get_cookie(resp.request, resp))
    w.fetch("http://www.google.com", callback_test)


class Fetcher(object):
    def __init__(self):
        self._cookies = ''
        self.cookiejar = requests.cookies.RequestsCookieJar()
        self._req_params = {}

    def pre_request(self, req, *args, **kwargs):
        # set cookies
        # 参数中已经提交了cookies
        cookie = cookies.dict_to_cookie(self.cookiejar)
        req.headers.update({'Cookie': cookie})


    def post_request(self, req, resp, *args, **kwargs):
        # set cookies
        cookies.make_cookiejar(self.cookiejar, req, resp)

    def test(self, *args):
        print args

    def init_request(self, session, url, **kwargs):
        req = session

        # set default parameters
        session.follow_redirects = False # 禁止跳转

        # set url
        req.url = url

        # method
        session.method = kwargs.get('method', 'GET')



        # (payload) data
        if 'data' in kwargs:
            if isinstance(kwargs['data'], dict):
                raise TypeError('Parameter data must be dict')

            payload = urllib.urlencode(kwargs['data'])
            session.body = payload

        if session.method == "POST"and not session.body:
            session.body = " "

        # set default header
        req.headers.update({'User-Agent': kwargs.get('user-agent', 'Mozilla/5.0 PyCrawler')})

        # update specified cookies
        if 'cookies' in kwargs:
            if isinstance(kwargs['cookies'], dict):
                raise TypeError('Cookies parameter must be instance of dict')

            for k, v in kwargs['cookies']:
                self.cookiejar[k] = v

        # update headers
        req.headers.update(kwargs.get('headers', {}))

        # params
        # Only: method/max_redirects


    @gen.coroutine
    def fetch(self, url, **kwargs):
        # init HTTPRequest
        session = HTTPRequest('', follow_redirects=False)
        self.init_request(session, url, **kwargs)

        instance_parameters = copy.deepcopy(self._req_params) # 参数

        http_client = AsyncHTTPClient()


        while True:
            self.pre_request(session, url, **kwargs)
            try:
                response = yield http_client.fetch(session, **instance_parameters)
                break
            except HTTPError as httperr:
                # redirects handler
                if httperr.code > 300 and httperr.code < 400:
                    self.post_request(session, httperr.response, url, **kwargs)
                    session.url = httperr.response.effective_url


        del instance_parameters
        self.post_request(session, response, url, **kwargs)

        raise gen.Return(response)




w = Fetcher()

"""
@gen.coroutine
def run():
    from pyquery import PyQuery as PQ
    print 'runed'
    kk = yield w.fetch("http://www.carters.com/carters-baby-girl-sets?startRow=0&sz=all")
    page = kk.body
    pq = PQ(page)
    data = []
    products = pq('li.grid-tile')
    for product in products:
        foo = PQ(product)
        data.append({'image': foo('img').attr('src'),
                     'link': foo('.name-link').attr('href'),
                     'title': foo('.name-link').text(),
                     'original_price': foo('.product-standard-price').text().replace('MSRP:', '').replace('$', '').strip(),
                     'sales_price':foo('.product-sales-price').text().replace('$', '').strip()
                     })



    import requests

    q = requests.post('http://127.0.0.1:8000/ezlookup/deal/?key=998998998', data={
        'website': 'carters',
        'currency': 'USD',
        'country': 'USA',
        'data': json.dumps(data)
    })
    print q
    #print bs.findAll('a', attrs={'class': 'name-link'})

run()
"""

@gen.coroutine
def run():
    print 'invoked'
    kk = yield w.fetch("http://127.0.0.1:8000", method="POST", body={})
    print kk
run()
#get("http://www.google.com", callback=callback_test)
tornado.ioloop.IOLoop.instance().start()
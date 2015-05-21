# coding=utf-8
import copy
import logging
import urllib
import tornado
from tornado import ioloop
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado import gen
import cookies
import requests
from log import fetch_logger


class Fetcher(object):
    def __init__(self):
        self._req_params = {}
        self.cookiejar = requests.cookies.RequestsCookieJar()

    def pre_request(self, req, *args, **kwargs):
        # set cookies
        # 参数中已经提交了cookies
        cookie = cookies.dict_to_cookie(self.cookiejar)
        req.headers.update({'Cookie': cookie})
        for k, v in kwargs.items():
            setattr(req, k, v)


    def post_request(self, req, resp, *args, **kwargs):
        # set cookies
        cookies.make_cookiejar(self.cookiejar, req, resp)

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


    def _get_HTTPRequest(url, **kwargs):
        return HTTPRequest(url, **kwargs)

    @gen.coroutine
    def fetch(self, url, **kwargs):
        # init HTTPRequest
        http_client = CurlAsyncHTTPClient()
        session = HTTPRequest('', follow_redirects=False)
        instance_parameters = copy.deepcopy(self._req_params) # 参数

        self.init_request(session, url, **kwargs)

        while True:

            self.pre_request(session, url=url, **kwargs)
            try:
                fetch_logger.info('{method} {url}'.format(method=session.method, url=session.url))
                response = yield http_client.fetch(session)
                fetch_logger.log_green('{code} {url}'.format(code=response.code, url=session.url))
                break
            except HTTPError as httperr:
                # redirects handler
                if httperr.code > 300 and httperr.code < 400:
                    fetch_logger.warning('{code} {url}'.format(code=httperr.code, url=session.url))
                    self.post_request(session, httperr.response, url, **kwargs)
                    url = httperr.response.headers.get('Location')
                else:
                    fetch_logger.error(httperr)
                    return


        del instance_parameters
        self.post_request(session, response, url, **kwargs)

        raise gen.Return(response)

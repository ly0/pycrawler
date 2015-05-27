import json
from pyquery import PyQuery

class Response(dict):
    PQ = PyQuery

    def __init__(self, resp, data_type):
        self._resp = resp
        self._type = data_type
        if data_type == 'json':
            self.update(json.loads(resp.body))
        elif data_type == 'html':
            self.body = resp.body
        self.code = resp.code

        # Origin URL


    def __call__(self, csspath):
        if self._type == 'html':
            return PyQuery(self.body)(csspath)
        else:
            return self

    def __repr__(self):
        if self._type == 'html':
            return '<HTTP Response %s: %s>' % (self.code, self._resp.effective_url)
        else:
            return super(Response, self).__repr__()
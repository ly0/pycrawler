from .base import BaseRPCParser, BaseRPCHandler
import jsonrpclib
from jsonrpclib.jsonrpc import isbatch, isnotification, Fault
from jsonrpclib.jsonrpc import dumps, loads


# self.handler

class JSONRPCParser(BaseRPCParser):

    content_type = 'application/json-rpc'

    def parse_request(self, request_body):
        try:
            request = loads(request_body)
        except:
            # Bad request formatting
            self.traceback()
            return self.faults.parse_error()
        self._requests = request
        self._batch = False
        request_list = []
        if isbatch(request):
            self._batch = True
            for req in request:
                req_tuple = (req['method'], req.get('params', []))
                request_list.append(req_tuple)
        else:
            self._requests = [request]
            request_list.append(
                (request['method'], request.get('params', []))
            )

        return tuple(request_list)

    def parse_responses(self, responses):
        if isinstance(responses, Fault):
            return dumps(responses)
        if len(responses) != len(self._requests):
            return dumps(self.faults.internal_error())
        response_list = []
        for i in range(0, len(responses)):
            request = self._requests[i]
            response = responses[i]
            if isnotification(request):
                # Even in batches, notifications have no
                # response entry
                continue
            rpcid = request['id']
            version = jsonrpclib.config.version
            if 'jsonrpc' not in request.keys():
                version = 1.0
            try:
                response_json = dumps(
                    response, version=version,
                    rpcid=rpcid, methodresponse=True
                )
            except TypeError:
                return dumps(
                    self.faults.server_error(),
                    rpcid=rpcid, version=version
                )
            response_list.append(response_json)
        if not self._batch:
            # Ensure it wasn't a batch to begin with, then
            # return 1 or 0 responses depending on if it was
            # a notification.
            if len(response_list) < 1:
                return ''
            return response_list[0]
        # Batch, return list
        return '[ %s ]' % ', '.join(response_list)


class JSONRPCLibraryWrapper(object):

    dumps = dumps
    loads = loads
    Fault = Fault


class JSONRPCHandler(BaseRPCHandler):
    """
    Subclass this to add methods -- you can treat them
    just like normal methods, this handles the JSON formatting.
    """
    _RPC_ = JSONRPCParser(JSONRPCLibraryWrapper)

#
# if __name__ == '__main__':
#     # Example Implementation
#     import sys
#     from tornadorpc.base import start_server
#     from tornadorpc.base import TestRPCHandler
#
#     class TestJSONRPC(TestRPCHandler):
#         _RPC_ = JSONRPCParser(JSONRPCLibraryWrapper)
#
#     port = 8181
#     if len(sys.argv) > 1:
#         port = int(sys.argv[1])
#
#     print 'Starting server on port %s' % port
#     start_server(TestJSONRPC, port=port)

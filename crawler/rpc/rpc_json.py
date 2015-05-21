from tornadorpc.json import JSONRPCHandler
from tornadorpc import private, start_server

class Tree(object):

    def power(self, base, power, modulo=None):
        result = pow(base, power, modulo)
        return result

    def _private(self):
        # Won't be callable
        return False

class Handler(JSONRPCHandler):

    tree = Tree()

    def add(self, x, y):
        return x+y

    def ping(self, obj):
        return obj

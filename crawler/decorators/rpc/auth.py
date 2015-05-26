"""
Decorators
"""

def authenticated(auth_func):

    def add_auth(func):
        func._need_authenticated = auth_func
        return func

    return add_auth
from crawler.ioloop import ioloop
from crawler.consumer import Consumer

import sys
import pkgutil
import os
import tasks
import inspect
from tornado.web import Application
from crawler.task import BaseTask
from crawler.rpc.rpc_json import Handler

TASK_LIST = {}

# launch RPC
WEBSERVER_PORT = 10000
application = Application([
    (r'/', Handler),
])

application.listen(WEBSERVER_PORT)


# find tasks
modules = [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(tasks.__file__)])]
api = {}

for module in modules:
    module_name = 'tasks.' + module
    __import__(module_name)
    foo = [i for i in sys.modules[module_name].__dict__.values() if inspect.isclass(i)
           and i != BaseTask
           and issubclass(i, BaseTask)]

    for task in foo:
        TASK_LIST[task.__name__] = task

    print '[API] load module:', foo

# register tasks
for k, v in TASK_LIST.items():
    setattr(Handler, k.lower(), v())



ioloop.start()

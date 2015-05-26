from crawler.ioloop import ioloop
from crawler.consumer import Consumer

import sys
import pkgutil
import os
import tasks

TASK_LIST =
# API modules dynamic loader

modules = [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(tasks.__file__)])]
api = {}

for module in modules:
    module_name = 'tasks.' + module
    __import__(module_name)
    api[module] = sys.modules[module_name].Api
    print '[API] load module:', module




#ioloop.start()
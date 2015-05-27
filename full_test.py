from crawler.task import BaseTask
from tornado import ioloop

class TestTask(BaseTask):
    pass

print TestTask._db
task = TestTask()
task.save({"id": 123, "data": "haha"})

ioloop.IOLoop.instance().start()

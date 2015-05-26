import motor
from tornado import gen
from tornado import ioloop


mongo_client = motor.MotorClient('localhost', 27017)


@gen.coroutine
def test():
    ret = yield mongo_client.database_names()
    print ret


test()
ioloop.IOLoop.instance().start()
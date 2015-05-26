class Meta(type):
    def __new__(cls, *args, **kwargs):
        pass


class Model(object):
    __metaclass__ = Meta


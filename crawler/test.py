from fetcher import Fetcher
from tornado import gen
import tornado


w = Fetcher()

@gen.coroutine
def run():
    print 'runed'
#    kk = yield w.fetch("http://www.abercrombie.cn/on/demandware.store/Sites-abercrombie_cn-Site/en_CN/Product-Variation?pid=anf-87741&dwvar_anf-87741_4MPrmry=4080&dwvar_anf-87741_color=01&Quantity=1&format=ajax&_=1431591378963")
    kk = yield w.fetch('http://127.0.0.1:8000')
    kk = yield w.fetch('http://127.0.0.1:8000', method="POST", headers={'User-Agent':'FUCK'})

run()

#get("http://www.google.com", callback=callback_test)
tornado.ioloop.IOLoop.instance().start()
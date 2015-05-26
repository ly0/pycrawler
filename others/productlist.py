import logging
import json
import re
import tornado
from crawler.task import BaseTask


class Carters(BaseTask):

    def on_start(self):
        pass

    def save(self, data):
        pass



class Taobao(BaseTask):
    def on_start(self):
        for i in range(5):
            self.fetch('http://tui.taobao.com/recommend?count=18&appid=%s&callback=jsonp' % str(i), next=self.test)

    def test(self, resp):
        print 'Done'
        try:
            json.loads(re.findall('jsonp\((.*?)\);', resp.body.decode('gbk'))[0])
            print resp._resp.effective_url
        except:
            pass

    def save(self, data):
        pass




t = Taobao()
tornado.ioloop.IOLoop.instance().run_sync(t.on_start)

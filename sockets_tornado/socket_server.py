import os, time
import tornado.httpserver, tornado.web, tornado.ioloop
from sockjs.tornado import SockJSConnection, SockJSRouter
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine
__STATIC__ = os.path.join(os.path.dirname(__file__), "tornado_static")


class MainPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("sock_test.html")


class AddConvertionWorker(tornado.web.RequestHandler):
    def get(self):
        self.write("AddConvertionWorker")


class ConvertionStatus(SockJSConnection):
    def __init__(self, *args, **kwargs):
        self.global_obj_key = ""
        SockJSConnection.__init__(self, *args, **kwargs)
        
    def on_message(self, msg):
        print("Got Message:", msg)
        val = 0
        while True:
            self.send(val)
            time.sleep(0.1)
            val += 1

    def on_open(self, data):
        print('Someone connected', self, data)


if __name__ == '__main__':

    WsRouter = SockJSRouter(ConvertionStatus, '/ws')

   # Sockets 
    ws_app = tornado.web.Application(WsRouter.urls)

    ws_app.listen(10666)
    application = tornado.web.Application([(r"/all_workers", MainPageHandler),
        (r"/tornado_static/(.*)", tornado.web.StaticFileHandler, {"path": __STATIC__}),
        (r'/add_convertion_worker', AddConvertionWorker)])
    application.listen(10667) 

    app = tornado.ioloop.IOLoop()
    app.instance().start()

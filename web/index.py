#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os

import tornado.web
import tornado.locks
from tornado.options import options

import config
from lib import db
#-----------------------------------------------------------------------
#   菅笠くんデータ on Web
#   index.py
#
#   菅笠くん on RaspberryPIで収集したデータを照会する
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
class BaseHandler(tornado.web.RequestHandler):
    pass



class HomeHandler(BaseHandler):
    async def get(self):
        pass



class WhereHandler(BaseHandler):
    async def get(self):
        pass



class WhenHandler(BaseHandler):
    async def get(self):
        pass



class SummaryHandler(BaseHandler):
    async def get(self):
        pass



class TraceHandler(BaseHandler):
    async def get(self):
        pass



class Application(tornado.web.Application):

    def __init__(self, db):
        self.db = db
        handlers = [
            (r"/", HomeHandler),
            (r"/where", WhereHandler),
            (r"/when", WhenHandler),
            (r"/summary", SummaryHandler),
            (r"/trace", TraceHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)



async def main():

    tornado.options.parse_command_line()

    mydb = db.Sugegasakun(config.LOCAL_DB)
    mydb.connect(config.HOST, config.DB, config.UID, config.PWD)

    app = Application(mydb)
    app.listen(config.HTTP_PORT)

    # In this demo the server will simply run until interrupted
    # with Ctrl-C, but if you want to shut down more gracefully,
    # call shutdown_event.set().
    shutdown_event = tornado.locks.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().run_sync(main)
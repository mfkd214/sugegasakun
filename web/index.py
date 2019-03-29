#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.locks
from tornado import gen
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
    
    def get(self):

        records = self.application.db.fill_new10()
        print("get")
        self.render("index.html",
                    records=records)



class WhereHandler(BaseHandler):
    def get(self):
        self.render("where.html",
                    month = "",
                    day = "",
                    year = "")



class WhenHandler(BaseHandler):
    def get(self):
        self.render("when.html",
                    keyword = "",
                    year = "",
                    month = "")



class SummaryHandler(BaseHandler):
    def get(self):
        self.render("summary.html")



class TraceHandler(BaseHandler):
    def get(self):
        self.render("trace.html")



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


def main():

    tornado.options.parse_command_line()

    mydb = db.Sugegasakun(config.LOCAL_DB)
    mydb.connect(config.HOST, config.DB, config.UID, config.PWD)

    app = Application(mydb)
    app.listen(config.HTTP_PORT)
    
    tornado.ioloop.IOLoop.current().start()



if __name__ == "__main__":
    main()

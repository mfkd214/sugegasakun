#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime
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

    def request_parse(self):
        self.graph_val_kb = "0"

        cnt = 0

        self.year = ""
        arg = self.get_arguments("year")
        if len(arg) > 0:
            cnt += 1
            self.year = arg[0]

        self.month = ""
        arg = self.get_arguments("month")
        if len(arg) > 0:
            cnt += 1
            self.month = arg[0]

        self.day = ""
        arg = self.get_arguments("day")
        if len(arg) > 0:
            cnt += 1
            self.day = arg[0]

        self.basho = ""
        arg = self.get_arguments("basho")
        if len(arg) > 0:
            cnt += 1
            self.basho = arg[0]

        return cnt



class HomeHandler(BaseHandler):
    
    def get(self):

        records = self.application.db.fill_new10()
        self.render("index.html",
                    records=records)



class WhereHandler(BaseHandler):
    def get(self):

        cnt = self.request_parse()
        print(cnt)
        if cnt == 0:
            self.month = str(datetime.now().month)

        records = None
        if self.day == "":
            records = self.application.db.fill_where_year_month(
                                            self.year, self.month)
        else:
            records = self.application.db.fill_where_week(
                                            self.year, self.month, self.day)

        self.render("where.html", 
                    month = self.month,
                    day = self.day,
                    year = self.year,
                    records = records )



class WhenHandler(BaseHandler):
    def get(self):

        self.request_parse()
        cnt = self.request_parse()
        if cnt == 0:
            self.month = str(datetime.now().month)

        records = self.application.db.fill_when(
                                        self.basho, self.year, self.month)

        self.render("when.html",
                    basho = self.basho,
                    year = self.year,
                    month = self.month,
                    records = records )



class SummaryHandler(BaseHandler):
    def get(self):

        self.request_parse()

        self.render("summary.html",
                    basho = self.basho,
                    year = self.year,
                    month = self.month,
                    day = self.day,
                    graph_val_kb = self.graph_val_kb)



class TraceHandler(BaseHandler):
    def get(self, ymd):
        zoom = 14
        size = "640x480"
        scale = 1
        maptype = "terrain"
        path = "color:0x000ff|weight:5"
        apikey = config.GMAP_APIKEY
        self.render("trace.html",
                    zoom = zoom,
                    size = size,
                    scale = scale,
                    maptype = maptype,
                    path = path,
                    key = apikey)



class Application(tornado.web.Application):

    def __init__(self, db):
        self.db = db
        handlers = [
            (r"/", HomeHandler),
            (r"/where", WhereHandler),
            (r"/when", WhenHandler),
            (r"/summary", SummaryHandler),
            (r"/trace/(.*)", TraceHandler),
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

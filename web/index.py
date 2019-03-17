#! /usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime
import tornado.ioloop
import tornado.web

from lib import sugegasakundata, db
#-----------------------------------------------------------------------
#   菅笠くん on Web
#   pi_index.py
#
#   菅笠くん on RaspberryPIのWEBサービス
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
_suge_dt = sugegasakundata.SugegasakunData(db.Db(False))
class IndexHandler(tornado.web.RequestHandler):
    """ /
    """
    def get(self):
        #-- 月
        now = datetime.now()
        month = str(now.month)

        #-- 場所
        keyword = ""

        #-- 画面表示
        self.render("index.html",
                    month = month,
                    keyword = keyword,
                    results = _suge_dt.search_of_month(month, keyword))



class MonthListHandler(tornado.web.RequestHandler):
    """ 検索ページ
    """
    def get(self, iMonth):

        #-- 月
        now = datetime.now()
        month = str(now.month)
        if iMonth != "0":
            month = iMonth

        #-- 場所        
        keyword = ""
        if "keyword" in self.request.arguments:
            tmp = self.request.arguments["keyword"]
            keyword = tmp[0].decode("utf-8")

        #-- 画面表示
        self.render("index.html",
                    month = month,
                    keyword = keyword,
                    results = _suge_dt.search_of_month(month, keyword))


class RangeListHandler(tornado.web.RequestHandler):
    """ 検索ページ > 日付クリック
    """
    def get(self, iKey):

        #-- Keyの先頭8文字を切り出す。
        ymd = iKey[:8]

        #-- 場所        
        keyword = ""
        if "keyword" in self.request.arguments:
            tmp = self.request.arguments["keyword"]
            keyword = tmp[0].decode("utf-8")

        month, results = _suge_dt.search_of_range(ymd, 15, keyword)

        #-- 画面表示
        self.render("index.html",
                    month = month,
                    keyword = keyword,
                    results = results)


class LocationHandler(tornado.web.RequestHandler):
    """ 検索ページ > 場所クリック
    """
    def get(self, iKey):

        month, date_range, basho_nm, summary_results, location, detail_results = \
            _suge_dt.get_map_details_data(iKey)
        #-- Map
        center  =   "{0},{1}".format(36.68656433333334, 139.46706666666665)
        zoom    =   14
        size    =   "{0}x{1}".format("640", "480")
        scale   =   1
        maptype =   "terrain"
        key     =   "AIzaSyDtG6AtHpHBvF6ooHys3ikNtmzruasZTrM"
        path    =   "color:0x0000ff|weight:5" + location 
        self.render("location.html",
                    month       =   month,
                    keyword     =   "",
                    searchkey   =   iKey,
                    center      =   center,
                    zoom        =   zoom,
                    size        =   size,
                    scale       =   scale,
                    maptype     =   maptype,
                    path        =   path,
                    key         =   key,
                    date_range  =   date_range,
                    basho_nm    =   basho_nm,
                    summary_results = summary_results,
                    detail_results  = detail_results,
                    data_url = "/location/" + iKey,
                    graph_url = "/location/" + iKey + "/graph")


class LocationGraphHandler(tornado.web.RequestHandler):
    """ 検索ページ > 場所 > グラフ
    """
    def get(self, iKey):
        print("LocationGraphHandler")
        month, date_range, basho_nm, summary_results, location, \
            alt_results, temp_results, hum_results, press_results = \
            _suge_dt.get_map_graph_data(iKey)
        #-- Map
        center  =   "{0},{1}".format(36.68656433333334, 139.46706666666665)
        zoom    =   14
        size    =   "{0}x{1}".format("640", "480")
        scale   =   1
        maptype =   "terrain"
        key     =   "AIzaSyDtG6AtHpHBvF6ooHys3ikNtmzruasZTrM"
        path    =   "color:0x0000ff|weight:5" + location 
        self.render("location_chart.html",
                    month       =   month,
                    keyword     =   "",
                    searchkey   =   iKey,
                    center      =   center,
                    zoom        =   zoom,
                    size        =   size,
                    scale       =   scale,
                    maptype     =   maptype,
                    path        =   path,
                    key         =   key,
                    date_range  =   date_range,
                    basho_nm    =   basho_nm,
                    summary_results = summary_results,
                    alt_results  = alt_results,
                    temp_results  = temp_results,
                    hum_results  = hum_results,
                    press_results  = press_results,
                    data_url = "/location/" + iKey,
                    graph_url = "/location/" + iKey + "/graph")



if __name__ == "__main__":
    import sys
    import os
    def make_app():
        return tornado.web.Application([
            (r"/", IndexHandler),
            (r"/monthlist/(.*)", MonthListHandler),
            (r"/rangelist/(.*)", RangeListHandler),
            (r"/location/(.*)/graph", LocationGraphHandler),
            (r"/location/(.*)", LocationHandler),
            ],
            template_path=os.path.join(os.getcwd(), "templates"),
            static_path=os.path.join(os.getcwd(),   "static"))

    port = 8000
    argv = sys.argv
    if len(argv) > 1:
        port = int(argv[1])

    app = make_app()
    app.listen(port)

    tornado.ioloop.IOLoop.current().start()

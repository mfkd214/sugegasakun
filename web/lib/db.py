#! /usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import pymysql.cursors
import googlemaps
import lib.config as config

class Db(object):

    def __init__(self, is_local=False):

        if not is_local:
            # MySQL
            DB      = config.DB
            HOST    = config.HOST
            UID     = config.UID
            PWD     = config.PWD
            CHARSET = config.CHARSET
            self.conn = pymysql.connect(
                            db=DB,
                            host=HOST,
                            port = 3306,
                            user=UID,
                            passwd=PWD,
                            charset=CHARSET)
        self.gmaps = googlemaps.Client(config.GMAP_APIKEY)


    def fill_summary_of_month(self, iMonth, iKeyword):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   gpsdate" \
                + " , gpsdate_from" \
                + " , gpsdate_to" \
                + " , basho_nm" \
                + " , start_koudo" \
                + " , avg_ondo" \
                + " , avg_shitsudo" \
                + " , avg_kiatsu" \
                + " from" \
                + "   summary" \
                + " where 1 = 1"
            if iMonth != "00":
                cmd += " and substring(gpsdate, 6, 2) = '%s'" % iMonth
            if iKeyword != "":
                cmd += " and basho_nm like '%" + iKeyword + "%'"
                
            cmd += " order by" \
                 + "   substring(gpsdate, 6, 5), gpsdate_from"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


    def fill_summary_of_md_range(self, iMdFrom, iMdTo, iKeyword):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   gpsdate" \
                + " , gpsdate_from" \
                + " , gpsdate_to" \
                + " , basho_nm" \
                + " , start_koudo" \
                + " , avg_ondo" \
                + " , avg_shitsudo" \
                + " , avg_kiatsu" \
                + " from" \
                + "   summary" \
                + " where substring(gpsdate, 6, 5) >= '%s'" % iMdFrom \
                + " and   substring(gpsdate, 6, 5) <= '%s'" % iMdTo 
            if iKeyword != "":
                cmd += " and   basho_nm like '%" + iKeyword + "%'"
                
            cmd += " order by" \
                 + "   substring(gpsdate, 6, 5), gpsdate_from"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


    def fill_summary_of_gpsdate_from(self, iGpsdateFrom):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   gpsdate" \
                + " , gpsdate_from" \
                + " , gpsdate_to" \
                + " , basho_nm" \
                + " , start_koudo" \
                + " , avg_ondo" \
                + " , avg_shitsudo" \
                + " , avg_kiatsu" \
                + " from" \
                + "   summary" \
                + " where gpsdate_from = %s"
            cur.execute(cmd, (iGpsdateFrom,))
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


    def fill_gps_gpsdate_range(self, iDatetimeFrom, iDatetimeTo):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   g.filename" \
                + " , g.gpsdate" \
                + " , g.ido" \
                + " , g.keido" \
                + " , g.koudo" \
                + " , ifnull(f.ondo, 0.0)" \
                + " , ifnull(f.shitsudo, 0.0)" \
                + " , ifnull(f.kiatsu, 0.0)" \
                + " from" \
                + "   gpsdata g" \
                + " left join fielddata f" \
                + "   on f.filename = g.filename" \
                + " where g.gpsdate >= %s" \
                + " and   g.gpsdate <= %s" \
                + " and   g.ido > 0.0" \
                + " order by" \
                + "   g.gpsdate"
            cur.execute(cmd, (iDatetimeFrom, iDatetimeTo,))
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


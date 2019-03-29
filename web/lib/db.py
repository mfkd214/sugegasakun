#! /usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import pymysql.cursors

class Sugegasakun(object):

    def __init__(self, localdb):

        if localdb == "":
            # MySQL
            self.is_local = False
            self.conn = None

        else:
            # sqlite
            import sqlite3
            self.is_local = True
            self.conn = sqlite3.connect(localdb)


    def connect(self, host, db, uid, pwd):
        if not self.is_local:
            self.conn = pymysql.connect(
                            host=host,
                            db=db,
                            port = 3306,
                            user=uid,
                            passwd=pwd,
                            charset="utf8",
                            cursorclass=pymysql.cursors.DictCursor)


    def fill_new10(self):
        """
        """
        with self.conn.cursor() as cur:
            cmd = " SELECT" \
                + "   s.gpsymd" \
                + " , s.start_time" \
                + " , s.ended_time" \
                + " , cast(round(s.ondo_min, 0) as char) ondo_min" \
                + " , cast(round(s.ondo_max, 0) as char) ondo_max" \
                + " , cast(round(s.ondo_avg, 0) as char) ondo_avg" \
                + " , cast(round(s.shitsudo_min, 0) as char) shitsudo_min" \
                + " , cast(round(s.shitsudo_max, 0) as char) shitsudo_max" \
                + " , cast(round(s.shitsudo_avg, 0) as char) shitsudo_avg" \
                + " , cast(round(s.kiatsu_min, 2) as char) kiatsu_min" \
                + " , cast(round(s.kiatsu_max, 2) as char) kiatsu_max" \
                + " , cast(round(s.kiatsu_avg, 2) as char) kiatsu_avg" \
                + " , cast(round(s.uvindex_min, 1) as char) uvindex_min" \
                + " , cast(round(s.uvindex_max, 1) as char) uvindex_max" \
                + " , cast(round(s.uvindex_avg, 1) as char) uvindex_avg" \
                + " , cast(round(s.lux_min, 0) as char) lux_min" \
                + " , cast(round(s.lux_max, 0) as char) lux_max" \
                + " , cast(round(s.lux_avg, 0) as char) lux_avg" \
                + " , cast(round(s.koudo_min, 0) as char) koudo_min" \
                + " , cast(round(s.koudo_max, 0) as char) koudo_max" \
                + " , if (g.cnt = 1, g.basho_nm, concat(g.basho_nm, ' 等')) basho_nm" \
                + " from" \
                + "   summary s" \
                + " left outer join (" \
                + "   select gpsymd, MAX(basho_nm) basho_nm, count(*) cnt" \
                + "   from summary_places" \
                + "   group by gpsymd" \
                + " ) g" \
                + "   on g.gpsymd = s.gpsymd" \
                + " ORDER by" \
                + "   s.gpsymd DESC" \
                + " LIMIT 10"
            cur.execute(cmd)
            for row in cur.fetchall():
                print("row")
                yield row




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


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
            self._host = host
            self._db = db
            self._port = 3306
            self._uid = uid
            self._pwd = pwd
            self._charset = "utf8"

            self._open_connect()


    def _open_connect(self):

        if not self.is_local:

            if (self.conn is None):
                self.conn = pymysql.connect(
                                host = self._host,
                                db =  self._db,
                                port = self._port,
                                user = self._uid,
                                passwd = self._pwd,
                                charset = self._charset,
                                cursorclass=pymysql.cursors.DictCursor)

            elif (not self.conn.open):
                self.conn = pymysql.connect(
                                host = self._host,
                                db =  self._db,
                                port = self._port,
                                user = self._uid,
                                passwd = self._pwd,
                                charset = self._charset,
                                cursorclass=pymysql.cursors.DictCursor)


    def _listing_sql(self):
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

        return cmd


    def fill_new10(self):
        """
        """
        self._open_connect()

        with self.conn.cursor() as cur:
            cmd = self._listing_sql() \
                + " ORDER by" \
                + "   s.gpsymd DESC" \
                + " LIMIT 10"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row


    def fill_where_year_month(self, year, month):
        """
        """
        self._open_connect()

        q = ""
        if year == "":
            if month != "":
                q = "%-" + month.zfill(2) + "-%"
        else:
            q = year + "-"
            if month == "":
                q += "%"
            else:
                q += month.zfill(2) + "-%"

        with self.conn.cursor() as cur:
            cmd = self._listing_sql() \
                + " WHERE s.gpsymd like '" + q + "'" \
                + " ORDER by" \
                + "   substring(s.gpsymd, 6, 10)" \
                + ",  s.gpsymd"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row


    def fill_where_week(self, year, month, day):
        """
        """
        self._open_connect()

        if year == "":
            year = datetime.now().strftime("%Y")
        d = datetime(int(year), int(month), int(day), 0, 0, 0)
        df = d - timedelta(days=15)
        dt = d + timedelta(days=15)

        date_from = df.strftime("%m-%d")
        date_to = dt.strftime("%m-%d")

        with self.conn.cursor() as cur:
            cmd = self._listing_sql() \
                + " WHERE substring(s.gpsymd, 6, 10) >= %s" \
                + " AND   substring(s.gpsymd, 6, 10) <= %s" \
                + " ORDER by" \
                + "   substring(s.gpsymd, 6, 10)" \
                + ",  s.gpsymd"
            cur.execute(cmd, (date_from, date_to,))
            for row in cur.fetchall():
                yield row


    def fill_when(self, basho, year, month):
        """
        """
        self._open_connect()

        q = ""
        if year == "":
            if month != "":
                q = "%-" + month.zfill(2) + "-%"
        else:
            q = year + "-"
            if month == "":
                q += "%"
            else:
                q += month.zfill(2) + "-%"

        with self.conn.cursor() as cur:
            cmd = "SELECT * FROM (" \
                + self._listing_sql() \
                + ") x" \
                + " WHERE 1 = 1"
            if basho != "":
                cmd += " AND x.basho_nm like '%" + basho + "%'"
            if q != "":
                cmd += " AND x.gpsymd like '" + q + "'"
            cmd += " ORDER by" \
                +  "   substring(x.gpsymd, 6, 10)" \
                +  " , x.gpsymd"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row


    def fill_summary_places(self, ymd, start_time):

        self._open_connect()

        with self.conn.cursor() as cur:
            cmd = " SELECT" \
                + "   s.gpsymd" \
                + " , s.start_time" \
                + " , s.ended_time" \
                + " , s.basho_nm" \
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
                + " , s.gpsdate_from" \
                + " , s.gpsdate_to" \
                + " from" \
                + "   summary_places s" \
                + " where s.gpsymd = %s"
            if not start_time == "":
                cmd += " and   s.start_time = '" + start_time + "'"
            cmd += " order by" \
                +  "   s.start_time"
            cur.execute(cmd, (ymd,))
            for row in cur.fetchall():
                yield row


    def fill_gpsdata(self, gpsdate_from, gpsdate_to):

        self._open_connect()

        with self.conn.cursor() as cur:
            cmd = " SELECT * FROM gpsdata"  \
                + " WHERE gpsdate >= %s and gpsdate <= %s" \
                + " AND   ido > 0.0" \
                + " ORDER BY" \
                + "   gpsdate"
            cur.execute(cmd, (gpsdate_from, gpsdate_to,))
            for row in cur.fetchall():
                yield row


    def fill_graph_data(self, gpsdate_from, gpsdate_to):

        self._open_connect()

        with self.conn.cursor() as cur:
            cmd = " SELECT" \
                + "   g.filename" \
                + " , g.gpsdate" \
                + " , round(ifnull(g.koudo,    0.0), 0) koudo" \
                + " , round(ifnull(f.ondo,     0.0), 0) ondo" \
                + " , round(ifnull(f.shitsudo, 0.0), 0) shitsudo" \
                + " , round(ifnull(f.kiatsu,   0.0), 2) kiatsu" \
                + " , round(ifnull(u.uvindex,  0.0), 0) uvindex" \
                + " , round(ifnull(l.lux,      0.0), 0) lux" \
                + " FROM" \
                + "   gpsdata g" \
                + " left join fielddata f" \
                + "   on f.filename = g.filename" \
                + " left join uvindexdata u" \
                + "   on u.filename = g.filename" \
                + " left join luxdata l" \
                + "   on l.filename = g.filename" \
                + " WHERE gpsdate >= %s" \
                + " AND   gpsdate <= %s" \
                + " ORDER BY" \
                + "   gpsdate"
            cur.execute(cmd, (gpsdate_from, gpsdate_to,))
            for row in cur.fetchall():
                yield row

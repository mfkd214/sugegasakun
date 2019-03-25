#! /usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql.cursors
import lib.config as config

class Sugegasakun(object):

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
                            charset=CHARSET,
                            cursorclass=pymysql.cursors.DictCursor)


    def __del__(self):
        """
        """
        self.conn.rollback()
        self.conn.close()


    def commit(self):
        """
        """
        self.conn.commit()


    def rollback(self):
        """
        """
        self.conn.rollback()


    def import_gpsdata(self, filename, gpsdate, ido, keido, koudo):

        cur = self.conn.cursor()
        try:
            cmd = "delete from gpsdata" \
                + " where filename = %s" \
                + " and   gpsdate  = %s"
            cur.execute(cmd, (filename, gpsdate, ))
            
            cur = self.conn.cursor()
            cmd = "INSERT INTO gpsdata" \
                + "( filename" \
                + ", gpsdate" \
                + ", ido" \
                + ", keido" \
                + ", koudo" \
                + ") VALUES (" \
                + "  %s" \
                + ", %s" \
                + ", %s" \
                + ", %s" \
                + ", %s" \
                + ")"
            cur.execute(cmd, (filename, gpsdate, ido, keido, koudo,))
        finally:
            cur.close()


    def import_fielddata(self, filename, ondo, shitsudo, kiatsu):

        cur = self.conn.cursor()
        try:
            cmd = "delete from fielddata" \
                + " where filename = %s"
            cur.execute(cmd, (filename, ))
            
            cur = self.conn.cursor()
            cmd = "INSERT INTO fielddata" \
                + "( filename" \
                + ", ondo" \
                + ", shitsudo" \
                + ", kiatsu" \
                + ") VALUES (" \
                + "  %s" \
                + ", %s" \
                + ", %s" \
                + ", %s" \
                + ")"
            cur.execute(cmd, (filename, ondo, shitsudo, kiatsu,))
        finally:
            cur.close()


    def import_uvindexdata(self, filename, uvindex, vis, ir):

        cur = self.conn.cursor()
        try:
            cmd = "delete from uvindexdata" \
                + " where filename = %s"
            cur.execute(cmd, (filename, ))
            
            cur = self.conn.cursor()
            cmd = "INSERT INTO uvindexdata" \
                + "( filename" \
                + ", uvindex" \
                + ", vis" \
                + ", ir" \
                + ") VALUES (" \
                + "  %s" \
                + ", %s" \
                + ", %s" \
                + ", %s" \
                + ")"
            cur.execute(cmd, (filename, uvindex, vis, ir,))
        finally:
            cur.close()


    def import_luxdata(self, filename, lux, full, ir):
        cur = self.conn.cursor()
        try:
            cmd = "delete from luxdata" \
                + " where filename = %s"
            cur.execute(cmd, (filename, ))
            
            cur = self.conn.cursor()
            cmd = "INSERT INTO luxdata" \
                + "( filename" \
                + ", lux" \
                + ", full" \
                + ", ir" \
                + ") VALUES (" \
                + "  %s" \
                + ", %s" \
                + ", %s" \
                + ", %s" \
                + ")"
            cur.execute(cmd, (filename, lux, full, ir,))
        finally:
            cur.close()

    def fill_gpsdata(self):
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   filename" \
                + ",  gpsdate" \
                + " , ido" \
                + " , keido" \
                + " , koudo" \
                + " , substring(gpsdate, 1, 10)" \
                + " from" \
                + "  gpsdata" \
                + " where ido > 0.0" \
                + " order by" \
                + "    gpsdate"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()

    def fill_gpsdata_datetime_range(self, gpsdate_from, gpsdate_to):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   filename" \
                + " , gpsdate" \
                + " from" \
                + "  gpsdata" \
                + " where gpsdate >= %s" \
                + " and   gpsdate <  %s" \
                + " order by" \
                + "   gpsdate"
            cur.execute(cmd,(gpsdate_from, gpsdate_to))
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()

    def get_fielddatas(self, filename):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   ondo" \
                + " , shitsudo" \
                + " , kiatsu" \
                + " from" \
                + "  fielddata" \
                + " where filename = %s"
            cur.execute(cmd,(filename,))
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()

    def delete_summary(self):
        cur = self.conn.cursor()
        try:
            cmd = "delete from summary"
            cur.execute(cmd)
        finally:
            cur.close()

    def insert_summary(self, rec):
        cur = self.conn.cursor()
        try:           
            cur = self.conn.cursor()
            cmd = "INSERT INTO summary" \
                + "( gpsdate, gpsdate_from , gpsdate_to" \
                + ", filename_from, filename_to" \
                + ", start_ido, start_keido, start_koudo, basho_nm" \
                + ", avg_ondo, avg_shitsudo, avg_kiatsu" \
                + ") VALUES (" \
                + "  %s, %s, %s" \
                + ", %s, %s" \
                + ", %s, %s, %s, %s" \
                + ", %s, %s, %s" \
                + ")"
            cur.execute(cmd, (
                    rec[5], rec[1], rec[10],
                    rec[0], rec[11],
                    rec[2], rec[3], rec[4], rec[6],
                    rec[7], rec[8], rec[9],))
        finally:
            cur.close()


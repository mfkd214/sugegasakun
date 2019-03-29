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


    def import_filename_gpsdata(self):
        """
        """
        cur = self.conn.cursor()
        try:
            cmd = "delete from filename_gpsdate"
            cur.execute(cmd)
            
            cur = self.conn.cursor()
            cmd = "insert into filename_gpsdate " \
                + "select " \
                + "  uni.`filename` " \
                + ", gps.`gpsdate` " \
                + "from ( " \
                + "  select filename from fielddata union " \
                + "  select filename from gpsdata   union " \
                + "  select filename from luxdata   union " \
                + "  select filename from uvindexdata " \
                + ") uni " \
                + "left outer join gpsdata gps " \
                + "  on gps.filename = uni.filename"
            cur.execute(cmd)
        finally:
            cur.close()


    def patch_filename_gpsdata(self):
        """
        PATCH.1
            2018以降、ファイル名と日時は合っているはずなのでGPS不良のため
            データが取得できていなくてもGPS日時は更新してしまう
        PATCH.2
            電源切り忘れによる不要データの削除
        """
        cur = self.conn.cursor()
        try:
            # PATCH.1
            cmd = "select filename from filename_gpsdate " \
                + "where filename > '20180331' "  \
                + "and   gpsdate is null"
            cur.execute(cmd)

            for row in cur.fetchall():
                filename = row["filename"]
                gpsdate = "%s-%s-%s %s:%s:%s" % (filename[0:4],
                                                 filename[4:6],
                                                 filename[6:8],
                                                 filename[8:10],
                                                 filename[10:12],
                                                 filename[12:])

                cur = self.conn.cursor()
                cmd = "update filename_gpsdate " \
                    + "set gpsdate = %s "  \
                    + "where filename = %s "
                cur.execute(cmd, (gpsdate, filename,))

            # PATCH.2
            cur = self.conn.cursor()
            cmd = "DELETE FROM filename_gpsdate " \
                + "WHERE '2017-05-27 16:30:00' < gpsdate " \
                + "AND   '2017-05-27 99:99:99' > gpsdate "
            cur.execute(cmd)

            cur = self.conn.cursor()
            cmd = "DELETE FROM filename_gpsdate " \
                + "WHERE '2018-09-22 15:06:00' < gpsdate " \
                + "AND   '2018-09-22 99:99:99' > gpsdate "
            cur.execute(cmd)

        finally:
            cur.close()


    def delete_summary(self):
        cur = self.conn.cursor()
        try:
            cmd = "delete from summary"
            cur.execute(cmd)
        finally:
            cur.close()

    
    def get_date(self):
        cur = self.conn.cursor()
        try:
            cmd = " SELECT distinct " \
                + "   substring(gpsdate, 1, 10) gps_ymd " \
                + " FROM " \
                + "   filename_gpsdate " \
                + " WHERE gpsdate is not null" \
                + " ORDER BY " \
                + "   substring(gpsdate, 1, 10)"
            cur.execute(cmd)
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


    def fill_all_datas_gpsymd(self, ymd):
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   fg.filename" \
                + " , fg.gpsdate" \
                + " , ifnull(gps.ido, 0.0) ido" \
                + " , ifnull(gps.keido, 0.0) keido" \
                + " , ifnull(gps.koudo, 0.0) koudo" \
                + " , ifnull(fi.ondo, 0.0) ondo" \
                + " , ifnull(fi.shitsudo, 0.0) shitsudo" \
                + " , ifnull(fi.kiatsu, 0.0) kiatsu" \
                + " , ifnull(uv.uvindex, 0.0) uvindex" \
                + " , ifnull(lx.lux, 0.0) lux" \
                + " , substring(fg.gpsdate, 1, 10) gps_ymd" \
                + " from" \
                + "  filename_gpsdate fg" \
                + " left join gpsdata gps" \
                + "   on gps.filename = fg.filename" \
                + " left outer join fielddata fi" \
                + "   on fi.filename = fg.filename" \
                + " left outer join uvindexdata uv" \
                + "   on uv.filename = fg.filename" \
                + " left outer join luxdata lx" \
                + "   on lx.filename = fg.filename" \
                + " where fg.gpsdate is not null" \
                + " and   substring(fg.gpsdate, 1, 10) = %s " \
                + " order by" \
                + "   fg.gpsdate" 
            cur.execute(cmd, (ymd,))
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


    def import_summary(self, 
                gps_ymd, start_time, ended_time,
                ondo_per_day, minondo_per_day, maxondo_per_day,
                shitsudo_per_day, minshitsudo_per_day, maxshitsudo_per_day,
                kiatsu_per_day, minkiatsu_per_day, maxkiatsu_per_day,
                uxindex_per_day, minuvindex_per_day, maxuvindex_per_day,
                lux_per_day, minlux_per_day, maxlux_per_day, 
                minkoudo_per_day, maxkoudo_per_day):

        cur = self.conn.cursor()
        try:
            cur = self.conn.cursor()
            cmd = "INSERT INTO summary (" \
                + "  gpsymd, start_time, ended_time" \
                + ", ondo_avg, ondo_min, ondo_max" \
                + ", shitsudo_avg, shitsudo_min, shitsudo_max" \
                + ", kiatsu_avg, kiatsu_min, kiatsu_max" \
                + ", uvindex_avg, uvindex_min, uvindex_max" \
                + ", lux_avg, lux_min, lux_max" \
                + ", koudo_min, koudo_max" \
                + ") VALUES (" \
                + "  %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s" \
                + ")"
            cur.execute(cmd, (
                    gps_ymd, start_time, ended_time,
                    ondo_per_day, minondo_per_day, maxondo_per_day,
                    shitsudo_per_day, minshitsudo_per_day, maxshitsudo_per_day,
                    kiatsu_per_day, minkiatsu_per_day, maxkiatsu_per_day,
                    uxindex_per_day, minuvindex_per_day, maxuvindex_per_day,
                    lux_per_day, minlux_per_day, maxlux_per_day, 
                    minkoudo_per_day, maxkoudo_per_day,))
        finally:
            cur.close()


    def delete_summary_place(self):
        cur = self.conn.cursor()
        try:
            cmd = "delete from summary_places"
            cur.execute(cmd)
        finally:
            cur.close()


    def fill_all_datas_gpsdate_range(self, gpsdate_fr, gpsdate_to):
        cur = self.conn.cursor()
        try:
            cmd = " select" \
                + "   fg.filename" \
                + " , fg.gpsdate" \
                + " , ifnull(gps.ido, 0.0) ido" \
                + " , ifnull(gps.keido, 0.0) keido" \
                + " , ifnull(gps.koudo, 0.0) koudo" \
                + " , ifnull(fi.ondo, 0.0) ondo" \
                + " , ifnull(fi.shitsudo, 0.0) shitsudo" \
                + " , ifnull(fi.kiatsu, 0.0) kiatsu" \
                + " , ifnull(uv.uvindex, 0.0) uvindex" \
                + " , ifnull(lx.lux, 0.0) lux" \
                + " , substring(fg.gpsdate, 1, 10) gps_ymd" \
                + " from" \
                + "  filename_gpsdate fg" \
                + " left join gpsdata gps" \
                + "   on gps.filename = fg.filename" \
                + " left outer join fielddata fi" \
                + "   on fi.filename = fg.filename" \
                + " left outer join uvindexdata uv" \
                + "   on uv.filename = fg.filename" \
                + " left outer join luxdata lx" \
                + "   on lx.filename = fg.filename" \
                + " where fg.gpsdate is not null" \
                + " and   fg.gpsdate >= %s " \
                + " and   fg.gpsdate <  %s " \
                + " order by" \
                + "   fg.gpsdate" 
            cur.execute(cmd, (gpsdate_fr, gpsdate_to, ))
            for row in cur.fetchall():
                yield row
        finally:
            cur.close()


    def import_summary_place(self, 
                gps_ymd, start_time, ended_time,
                ido, keido, basho_nm,
                ondo_per_day, minondo_per_day, maxondo_per_day,
                shitsudo_per_day, minshitsudo_per_day, maxshitsudo_per_day,
                kiatsu_per_day, minkiatsu_per_day, maxkiatsu_per_day,
                uxindex_per_day, minuvindex_per_day, maxuvindex_per_day,
                lux_per_day, minlux_per_day, maxlux_per_day, 
                minkoudo_per_day, maxkoudo_per_day,
                gpsdate_from, gpsdate_to,
                filename_from, filename_to):

        cur = self.conn.cursor()
        try:
            cur = self.conn.cursor()
            cmd = "INSERT INTO summary_places (" \
                + "  gpsymd, start_time, ended_time" \
                + ", ido, keido, basho_nm" \
                + ", ondo_avg, ondo_min, ondo_max" \
                + ", shitsudo_avg, shitsudo_min, shitsudo_max" \
                + ", kiatsu_avg, kiatsu_min, kiatsu_max" \
                + ", uvindex_avg, uvindex_min, uvindex_max" \
                + ", lux_avg, lux_min, lux_max" \
                + ", koudo_min, koudo_max" \
                + ", gpsdate_from, gpsdate_to" \
                + ", filename_from, filename_to" \
                + ") VALUES (" \
                + "  %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s, %s" \
                + ", %s, %s" \
                + ", %s, %s" \
                + ", %s, %s" \
                + ")"
            cur.execute(cmd, (
                    gps_ymd, start_time, ended_time,
                    ido, keido, basho_nm,
                    ondo_per_day, minondo_per_day, maxondo_per_day,
                    shitsudo_per_day, minshitsudo_per_day, maxshitsudo_per_day,
                    kiatsu_per_day, minkiatsu_per_day, maxkiatsu_per_day,
                    uxindex_per_day, minuvindex_per_day, maxuvindex_per_day,
                    lux_per_day, minlux_per_day, maxlux_per_day, 
                    minkoudo_per_day, maxkoudo_per_day,
                    gpsdate_from, gpsdate_to,
                    filename_from, filename_to,))
        finally:
            cur.close()


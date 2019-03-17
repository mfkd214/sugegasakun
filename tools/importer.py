#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import pymysql.cursors
import googlemaps
from gpsfile import Gpsfile
from fieldfile import Fieldfile
import config
class SugegasakunDB(object):

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



gmaps = googlemaps.Client(config.GMAP_APIKEY)
_db = SugegasakunDB()

def _cut_extention(filename):
    """
    """
    tmp = filename.split(".")
    return tmp[0]


def import_datas(data_dir):
    """
    """
    if not os.path.exists(data_dir):
        print("path not found", data_dir)
        return 4

    for f in os.listdir(data_dir):
        filename = os.path.join(data_dir, f)
        if not os.path.isfile(filename):
            continue

        if f.find("gps.txt") >= 0:
            gps = Gpsfile(filename)
            if gps.jst != None:
                _db.import_gpsdata(
                        _cut_extention(f),
                        gps.jst,
                        gps.ido,
                        gps.keido,
                        gps.koudo)
                _db.commit()
            
        elif f.find("field.txt") >= 0:
            field = Fieldfile(filename)
            if field.ondo > 0.0 and field.shitsudo > 0.0 and field.kiatsu > 0.0:
                _db.import_fielddata(
                        _cut_extention(f),
                        field.ondo,
                        field.shitsudo,
                        field.kiatsu)
                _db.commit()

        else:
            continue


def _get_location_name(ido, keido):
    """ 場所名取得
    """
    res = gmaps.reverse_geocode(
                    (ido, keido),
                    language="ja",
                    result_type="locality|sublocality",
                    location_type="APPROXIMATE")
    return res[0]["formatted_address"]


def _is_long_distance(
        pre_datetime, pre_ido, pre_keido, now_datetime, ido, keido):
    """ 直前の緯度、経度から離れている場合、違う場所と判定する
            緯度が0.01差がある(1.11km離れている)
    """
    sa = pre_ido - ido
    if abs(sa) > 0.005:
        return True
    return False


def _generate_start_points():
    """
    """
    start_points = list()
    brk_ymd = ""
    pre_datetime = ""
    pre_ido = 0.0
    pre_keido = 0.0
    for r in _db.fill_gpsdata():
        # 日付ブレイク
        if brk_ymd != r[5]:
            brk_ymd = r[5]
            pre_datetime = r[1]
            pre_ido = r[2]
            pre_keido = r[3]
            start_points.append([
                r[0], r[1], r[2], r[3], r[4], r[5],
                    _get_location_name(r[2], r[3])])
            continue

        # 直前のレコードと距離が離れている場合、場所が違うと判定
        if _is_long_distance(
                pre_datetime, pre_ido, pre_keido,
                r[1], r[2], r[3]):
            brk_ymd = r[5]
            pre_datetime = r[1]
            pre_ido = r[2]
            pre_keido = r[3]
            start_points.append([
                r[0], r[1], r[2], r[3], r[4], r[5],
                    _get_location_name(r[2], r[3])])
            continue

        pre_datetime = r[1]
        pre_ido = r[2]
        pre_keido = r[3]

    return start_points


def _generate_avgs_and_lastdate(fromDate, toDate):
    """
    """
    last_filename = ""
    last_datetime = ""
    avg_ondo = 0.0
    avg_shitsudo = 0.0
    avg_kiatsu = 0.0
    
    ondos = list()
    shitsudos = list()
    kiatsus = list()
    for gps_r in _db.fill_gpsdata_datetime_range(fromDate, toDate):
        last_filename = gps_r[0]
        last_datetime = gps_r[1]

        # 温度、湿度、気圧を取得
        for field_r in _db.get_fielddatas(gps_r[0]):
            if field_r[0] > 0:
                ondos.append(field_r[0])
            if field_r[1] > 0:
                shitsudos.append(field_r[1])
            if field_r[2] > 0:
                kiatsus.append(field_r[2])

        # 平均（温度、湿度、気圧）
        if len(ondos) > 0:
            avg_ondo = sum(ondos) / len(ondos)
            
        if len(shitsudos) > 0:
            avg_shitsudo = sum(shitsudos) / len(shitsudos)

        if len(kiatsus) > 0:
            avg_kiatsu = sum(kiatsus) / len(kiatsus)

    return avg_ondo, avg_shitsudo, avg_kiatsu, \
            last_datetime, last_filename 


def create_summary():
    """
    """
    _db.delete_summary()
    _db.commit()
    
    # 開始地点の情報をリストアップ
    start_points = _generate_start_points()

    # 開始地点から次のレコードまでの平均（気温、湿度、気圧）と最終日時を追加
    for idx, r in enumerate(start_points):
        fr_nichiji = r[1]
        to_nichiji = ""
        if idx + 1 == len(start_points):
            # リストの最終行
            to_nichiji = "%s99:99:99" % fr_nichiji[:11]
        else:
            # 日付が変わっていたら、その日の99:99:99
            if start_points[idx + 1][1][:11] == fr_nichiji[:11]:
                to_nichiji = start_points[idx + 1][1]
            else:
                to_nichiji = "%s99:99:99" % fr_nichiji[:11]

        # 該当期間の平均と該当期間の最終日時取得
        ondo, shitsudo, kiatsu, lastdate, filename = \
            _generate_avgs_and_lastdate(fr_nichiji, to_nichiji)
        r.append(ondo)
        r.append(shitsudo)
        r.append(kiatsu)
        r.append(lastdate)
        r.append(filename)

        # DB Insert
        _db.insert_summary(r)
        _db.commit()



if __name__ == "__main__":
    create_summary()

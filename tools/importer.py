#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
from lib import db, gpsfile, fieldfile, uvindexfile, luxfile, gmaps

class Impoter(object):

    def __init__(self, is_local):
        self.db = db.Sugegasakun(is_local)


    def _cut_extention(self, filename):
        """
        """
        tmp = filename.split(".")
        return tmp[0]


    def _is_long_distance(self, pre_datetime, pre_ido, pre_keido, now_datetime, ido, keido):
        """ 直前の緯度、経度から離れている場合、違う場所と判定する
            緯度が0.01差がある(1.11km離れている)
        """
        sa = pre_ido - ido
        if abs(sa) > 0.005:
            return True
        return False


    def _generate_start_points(self):
        """
        """
        maps = gmaps.Gmaps()

        start_points = list()
        brk_ymd = ""
        pre_datetime = ""
        pre_ido = 0.0
        pre_keido = 0.0
        for r in self.db.fill_gpsdata():
            # 日付ブレイク
            if brk_ymd != r[5]:
                brk_ymd = r[5]
                pre_datetime = r[1]
                pre_ido = r[2]
                pre_keido = r[3]
                start_points.append([
                    r[0], r[1], r[2], r[3], r[4], r[5],
                        maps.location_name(r[2], r[3])])
                continue

            # 直前のレコードと距離が離れている場合、場所が違うと判定
            if self._is_long_distance(
                    pre_datetime, pre_ido, pre_keido, r[1], r[2], r[3]):
                brk_ymd = r[5]
                pre_datetime = r[1]
                pre_ido = r[2]
                pre_keido = r[3]
                start_points.append([
                    r[0], r[1], r[2], r[3], r[4], r[5],
                        maps.location_name(r[2], r[3])])
                continue

            pre_datetime = r[1]
            pre_ido = r[2]
            pre_keido = r[3]

        return start_points


    def _generate_avgs_and_lastdate(self, fromDate, toDate):
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
        for gps_r in self.db.fill_gpsdata_datetime_range(fromDate, toDate):
            last_filename = gps_r[0]
            last_datetime = gps_r[1]

            # 温度、湿度、気圧を取得
            for field_r in self.db.get_fielddatas(gps_r[0]):
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


    def import_datas(self, data_dir):
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
                gps = gpsfile.Gpsfile(filename)
                if gps.jst != None:
                    self.db.import_gpsdata(
                                    self._cut_extention(f),
                                    gps.jst,
                                    gps.ido,
                                    gps.keido,
                                    gps.koudo)
                    self.db.commit()
                
            elif f.find("field.txt") >= 0:
                field = fieldfile.Fieldfile(filename)
                if field.ondo > 0.0 and field.shitsudo > 0.0 and field.kiatsu > 0.0:
                    self.db.import_fielddata(
                                    self._cut_extention(f),
                                    field.ondo,
                                    field.shitsudo,
                                    field.kiatsu)
                    self.db.commit()

            elif f.find("uvindex.txt") >= 0:
                uvindex = uvindexfile.UVIndexfile(filename)
                if uvindex.uv_index > 0.0 and uvindex.vis > 0.0 and uvindex.ir > 0.0:
                    self.db.import_uvindexdata(
                                    self._cut_extention(f),
                                    uvindex.uv_index,
                                    uvindex.vis,
                                    uvindex.ir)
                    self.db.commit()

            elif f.find("lux.txt") >= 0:
                lux = luxfile.Luxfile(filename)
                if lux.lux > 0.0 and lux.full > 0.0 and lux.ir > 0.0:
                    self.db.import_luxdata(
                                    self._cut_extention(f),
                                    lux.lux,
                                    lux.full,
                                    lux.ir)
                    self.db.commit()


            else:
                continue


    def create_summary(self):
        """
        """
        self.db.delete_summary()
        self.db.commit()
        
        # 開始地点の情報をリストアップ
        start_points = self._generate_start_points()

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
                self._generate_avgs_and_lastdate(fr_nichiji, to_nichiji)
            r.append(ondo)
            r.append(shitsudo)
            r.append(kiatsu)
            r.append(lastdate)
            r.append(filename)

            # DB Insert
            self.db.insert_summary(r)
            self.db.commit()



if __name__ == "__main__":
    imp = Impoter(False)

    imp.import_datas("/Users/mfkd214/Documents/sugegasakun_data_unzip/20190324")

    #imp.create_summary()
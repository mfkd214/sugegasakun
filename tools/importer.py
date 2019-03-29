#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
from lib import db, gpsfile, fieldfile, uvindexfile, luxfile, gmaps, summary

class Impoter(object):

    def __init__(self, is_local):
        self.db = db.Sugegasakun(is_local)


    def _cut_extention(self, filename):
        """
        """
        tmp = filename.split(".")
        return tmp[0]


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

        self.db.import_filename_gpsdata()
        self.db.patch_filename_gpsdata()
        self.db.commit()


    def create_summary(self):
        """
        """
        self.db.delete_summary()
        self.db.commit()

        # 日付取得
        for ymd in self.db.get_date():

            smry = summary.Summary(ymd["gps_ymd"])

            # 日付に一致する各種データを取得
            for rec in self.db.fill_all_datas_gpsymd(ymd["gps_ymd"]):

                smry.stack(rec)

            # 追加
            self.db.import_summary(
                        ymd["gps_ymd"],
                        smry.start_time,
                        smry.ended_time,
                        smry.avgondo_per_day(),
                        smry.minondo_per_day(),
                        smry.maxondo_per_day(),
                        smry.avgshitsudo_per_day(),
                        smry.minshitsudo_per_day(),
                        smry.maxshitsudo_per_day(),
                        smry.avgkiatsu_per_day(),
                        smry.minkiatsu_per_day(),
                        smry.maxkiatsu_per_day(),
                        smry.avguvindex_per_day(),
                        smry.minuvindex_per_day(),
                        smry.maxuvindex_per_day(),
                        smry.avglux_per_day(),
                        smry.minlux_per_day(),
                        smry.maxlux_per_day(), 
                        smry.minkoudo_per_day(),
                        smry.maxkoudo_per_day())
            self.db.commit()


    def _is_long_distance(self, pre_datetime, pre_ido, pre_keido, now_datetime, ido, keido):
        """ 直前の緯度、経度から離れている場合、違う場所と判定する
            緯度が0.01差がある(1.11km離れている)
        """
        sa = pre_ido - ido
        if abs(sa) > 0.01:
            return True
        return False


    def create_summary_place(self):
        """
        """
        maps = gmaps.Gmaps()
        start_points = list()

        self.db.delete_summary_place()
        self.db.commit()

        # 日付取得
        for ymd in self.db.get_date():

            # 日付に一致する各種データを取得
            pre_datetime = ""
            pre_ido = 0.0
            pre_keido = 0.0
            for rec in self.db.fill_all_datas_gpsymd(ymd["gps_ymd"]):

                # 位置情報があるものだけ対象にする
                if rec["ido"] == 0:
                    continue

                # 1件目
                if pre_datetime == "":
                    pre_datetime = rec["gpsdate"]
                    pre_ido = rec["ido"]
                    pre_keido = rec["keido"]

                    start_point = dict()
                    start_point["filename"] = rec["filename"]
                    start_point["start_gpsdate"] = rec["gpsdate"]
                    start_point["ido"] = rec["ido"]
                    start_point["keido"] = rec["keido"]
                    start_point["basho_nm"] = maps.location_name(rec["ido"], rec["keido"])
                    start_points.append(start_point)
                    continue

                # 直前のレコードと距離が離れている場合、場所が違うと判定
                if self._is_long_distance(
                                pre_datetime, pre_ido, pre_keido,
                                rec["gpsdate"], rec["ido"], rec["keido"]):

                    pre_datetime = rec["gpsdate"]
                    pre_ido = rec["ido"]
                    pre_keido = rec["keido"]

                    start_point = dict()
                    start_point["filename"] = rec["filename"]
                    start_point["start_gpsdate"] = rec["gpsdate"]
                    start_point["ido"] = rec["ido"]
                    start_point["keido"] = rec["keido"]
                    start_point["basho_nm"] = maps.location_name(rec["ido"], rec["keido"])
                    start_points.append(start_point)
                    continue

                pre_datetime = rec["gpsdate"]
                pre_ido = rec["ido"]
                pre_keido = rec["keido"]


        # 開始地点から次のレコードまでの平均（気温、湿度、気圧、uvindex, lux）と最終日時を追加
        for idx, start_point in enumerate(start_points):
            fr_nichiji = start_point["start_gpsdate"]
            to_nichiji = ""
            if idx + 1 == len(start_points):
                # リストの最終行
                to_nichiji = "%s99:99:99" % fr_nichiji[:11]
            else:
                # 日付が変わっていたら、その日の99:99:99
                if start_points[idx + 1]["start_gpsdate"][:11] == fr_nichiji[:11]:
                    to_nichiji = start_points[idx + 1]["start_gpsdate"]
                else:
                    to_nichiji = "%s99:99:99" % fr_nichiji[:11]

            # スタック
            smry = summary.Summary(fr_nichiji[:10])
            for rec in self.db.fill_all_datas_gpsdate_range(fr_nichiji, to_nichiji):
                smry.stack(rec)


            # 追加
            self.db.import_summary_place(
                        smry.gps_ymd,
                        smry.start_time,
                        smry.ended_time,
                        start_point["ido"],
                        start_point["keido"],
                        start_point["basho_nm"],
                        smry.avgondo_per_day(),
                        smry.minondo_per_day(),
                        smry.maxondo_per_day(),
                        smry.avgshitsudo_per_day(),
                        smry.minshitsudo_per_day(),
                        smry.maxshitsudo_per_day(),
                        smry.avgkiatsu_per_day(),
                        smry.minkiatsu_per_day(),
                        smry.maxkiatsu_per_day(),
                        smry.avguvindex_per_day(),
                        smry.minuvindex_per_day(),
                        smry.maxuvindex_per_day(),
                        smry.avglux_per_day(),
                        smry.minlux_per_day(),
                        smry.maxlux_per_day(), 
                        smry.minkoudo_per_day(),
                        smry.maxkoudo_per_day(),
                        smry.rows[0]["gpsdate"],
                        smry.rows[len(smry.rows) - 1]["gpsdate"],
                        smry.rows[0]["filename"],
                        smry.rows[len(smry.rows) - 1]["filename"])
            self.db.commit()



if __name__ == "__main__":
    import lib.config as config

    imp = Impoter(False)

    imp.import_datas(config.DATA_DIR)

    imp.create_summary()

    imp.create_summary_place()

import sys
import os
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import sqlite3
from lib import gpsfile, fieldfile, uvindexfile, luxfile, summary, gmaps, config
from lib import db as database
################################################################################
#   importer.py
#   各ファイルからDBに突っ込む
#
#   2019.04.--  mfkd    ThreadPoolExecutorを使用するように修正
#   2019.--.--  mfkd    new
################################################################################
def _cut_extention(fullpath):
    bn = os.path.basename(fullpath)
    tmp_l = bn.split(".")
    return tmp_l[0]


def import_gps(filename):

    try:
        gps = gpsfile.Gpsfile(filename)
        if gps.jst == None:
            return 1

        fn = _cut_extention(filename)
        with database.Sugegasakun(config.LOCALDB) as d:
            d.import_gpsdata(fn, gps.jst, gps.ido, gps.keido, gps.koudo)
            d.commit()
        return 0
    except:
        print("Error import_gps %s" % (filename))
        return 4


def import_field(filename):

    try:
        field = fieldfile.Fieldfile(filename)
        if field.ondo > 0.0 and field.shitsudo > 0.0 and field.kiatsu > 0.0:
            pass
        else:
            return 1

        fn = _cut_extention(filename)
        with database.Sugegasakun(config.LOCALDB) as d:
            d.import_fielddata(fn, field.ondo, field.shitsudo, field.kiatsu)
            d.commit()
        return 0
    except:
        print("Error import_field %s" % (filename))
        return 4


def import_uvindex(filename):

    try:
        uv = uvindexfile.UVIndexfile(filename)
        if uv.uv_index > 0.0 and uv.vis > 0.0 and uv.ir > 0.0:
            pass
        else:
            return 1

        fn = _cut_extention(filename)
        with database.Sugegasakun(config.LOCALDB) as d:
            d.import_uvindexdata(fn, uv.uv_index, uv.vis, uv.vis)
            d.commit()
        return 0

    except:
        print("Error import_uvindex %s" % (filename))
        return 4
    

def import_lux(filename):

    try:
        lux = luxfile.Luxfile(filename)
        if lux.lux > 0.0 and lux.full > 0.0 and lux.ir > 0.0:
            pass
        else:
            return 1

        fn = _cut_extention(filename)
        with database.Sugegasakun(config.LOCALDB) as d:
            d.import_luxdata(fn, lux.lux, lux.full, lux.ir)
            d.commit()
        return 0

    except:
        print("Error import_lux %s" % (filename))
        return 4


def import_files(filename):

    if filename.find("gps.txt") >= 0:
        import_gps(filename)

    elif filename.find("field.txt") >= 0:
        import_field(filename)

    elif filename.find("uvindex.txt") >= 0:
        import_uvindex(filename)

    elif filename.find("lux.txt") >= 0:
        import_lux(filename)

    else:
        pass
    

def generate_summary(gps_ymd):
    print(gps_ymd)

    try:
        with database.Sugegasakun(config.LOCALDB) as d:

            smry = summary.Summary(gps_ymd)

            # 日付に一致する各種データを取得
            for rec in d.fill_all_datas_gpsymd(gps_ymd):
                smry.stack(rec)

            # 追加
            d.import_summary(
                    gps_ymd,
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

            d.commit()
    except:
        print("summary", gps_ymd)
        print(sys.exc_info()[0])



def _is_long_distance(pre_datetime, pre_ido, pre_keido, now_datetime, ido, keido):
    """ 直前の緯度、経度から離れている場合、違う場所と判定する。
        （ちなみに、緯度が0.01差がある場合、1.11km離れている。経度は緯度による可変値)
        緯度差、経度差の斜辺値を元に同一場所判定する。とりあえず時間軸は考慮しない。
    """
    ido_sa = abs(pre_ido - ido)
    keido_sa = abs(pre_keido - keido)

    expo_ido_sa = ido_sa ** 2
    expo_keido_sa = keido_sa ** 2

    heihokon = math.sqrt(expo_ido_sa + expo_keido_sa)
    heihokon *= 1000

    # 斜辺が10.0の根拠はなし。実績値ベースでなんとなくな値。
    if heihokon > 10.0:
        return True
    return False


def generate_summary_place():
    """
    """

    maps = gmaps.Gmaps()
    start_points = list()

    with database.Sugegasakun(config.LOCALDB) as d:

        # 日付取得
        for ymd in d.get_date():

            # 日付に一致する各種データを取得
            pre_datetime = ""
            pre_ido = 0.0
            pre_keido = 0.0
            for rec in d.fill_all_datas_gpsymd(ymd["gps_ymd"]):

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
                if _is_long_distance(
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
            for rec in d.fill_all_datas_gpsdate_range(fr_nichiji, to_nichiji):
                smry.stack(rec)


            # 追加
            d.import_summary_place(
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
            d.commit()



def main():

    # files
    #---------------------------------------------------------------------------
    print(datetime.now(), "start import files...")
    max_worker = 4
    with ThreadPoolExecutor(max_workers=max_worker) as executor:

        for f in os.listdir(config.DATA_DIR):

            filename = os.path.join(config.DATA_DIR, f)
            if not os.path.isfile(filename):
                continue

            executor.submit(import_files, filename)

    print(datetime.now(), "done!")


    # filename_gpsdata
    #---------------------------------------------------------------------------
    print(datetime.now(), "start generate filename_gpsdata...")
    with database.Sugegasakun(config.LOCALDB) as d:

        d.import_filename_gpsdata()
        d.patch_filename_gpsdata()
        d.commit()

    print(datetime.now(), "done!")


    # summary
    #---------------------------------------------------------------------------
    print(datetime.now(), "start generate summary...")
    with database.Sugegasakun(config.LOCALDB) as d:
        d.delete_summary()
        d.commit()

        max_worker = 4
        with ThreadPoolExecutor(max_workers=max_worker) as executor:

            for ymd in d.get_date():
    
                executor.submit(generate_summary, ymd["gps_ymd"])

    print(datetime.now(), "done!")


    # generate_summary_places
    #---------------------------------------------------------------------------
    print(datetime.now(), "start generate summary_places...")
    with database.Sugegasakun(config.LOCALDB) as d:

        d.delete_summary_place()
        d.commit()

    generate_summary_place()
    print(datetime.now(), "done!")



if __name__ == "__main__":
    main()
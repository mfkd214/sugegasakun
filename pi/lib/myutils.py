#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import datetime
import subprocess
#-----------------------------------------------------------------------
#   RaspberryPI on 菅笠くん
#   myutils.py
#
#   RaspberryPI on 菅笠くんの共通関数
#
#   1.0.0   mfkd    Created
#-----------------------------------------------------------------------
def bool2str(iBool):
    """ ブール型の引数をOK|NGに変換
    """
    if iBool:
        return "OK"
    else:
        return "NG"


def get_sysdate_string():
    """ 現在システム日時をstr型のyyyymmddhhmi形式で返す
        Javascript側で使ってるんで注意。
        return str
    """
    now =   datetime.datetime.now()
    return now.strftime('%Y%m%d%H%M')


def get_formated_sysdate():
    """ 現在システム日時をstr型のyyyy.mm.dd hh:mi形式で返す
        return str
    """
    now =   datetime.datetime.now()
    return now.strftime('%Y.%m.%d %H:%M')


def is_scheduler_working(scheduler_start_file):
    """ スケジューラステータスを返す
        return str
    """
    if os.path.exists(scheduler_start_file):
        return True
    else:
        return False


def get_scheduler_status(scheduler_start_file):
    """ スケジューラステータスを返す
        return str
    """
    if is_scheduler_working(scheduler_start_file):
        return "稼働中"
    else:
        return "停止中"


def format_datetime(i_yyyymmddhhmiss,i_format_str):
    """ 引数をi_yyyymmddhhmissをi_format_strでフォーマットして返す
        return str
    """

    i_yyyymmddhhmiss += "00000000000000"
    try:

        d = datetime.datetime( \
                int(i_yyyymmddhhmiss[0:4]),
                int(i_yyyymmddhhmiss[4:6]),
                int(i_yyyymmddhhmiss[6:8]),
                int(i_yyyymmddhhmiss[8:10]),
                int(i_yyyymmddhhmiss[10:12]),
                int(i_yyyymmddhhmiss[12:14]))
        return d.strftime(i_format_str)

    except Exception as ex:
        return ""


def set_clock(i_yyyymmddhhmi):
    """ システム時刻を設定する
        return Bool
    """

    i_yyyymmddhhmi += "00000000000000"
    ts = format_datetime(i_yyyymmddhhmi[:14], "%m/%d %H:%M %Y")
    if ts == "":
        return False
    cmd = 'date -s "{0}"'.format(ts)
    os.system(cmd)

    return True


def shutdown(timer=1):
    """ OSをshutdownする
        return Bool
    """
    try:
        cmd = "shutdown -h now"
        print(cmd)
        os.system(cmd)
        return True
    except:
        return False


def change_scheduler_status(scheduler_stat_file):
    """
    """
    # ファイルがある場合は削除、ない場合は作成
    pre = os.path.exists(scheduler_stat_file)
    if pre:
        # rm
        res = subprocess.call(
                "rm %s" % scheduler_stat_file,
                shell=True)

    else:
        # touch
        res = subprocess.call(
                "touch %s" % scheduler_stat_file,
                shell=True)

    after = os.path.exists(scheduler_stat_file)
    if pre != after:
        return True
    else:
        return False


def get_sampling_log(sampling_data_dir, count=20):
    """ サンプリングデータの一覧を作成
    """
    files = list()
    for item in os.listdir(sampling_data_dir):
        if os.path.isfile(os.path.join(sampling_data_dir, item)):
            files.append(item)
    files.sort(reverse=True)

    ret = list()
    for i, f in enumerate(files):
        if i == count:
            break

        getsize = os.path.getsize(os.path.join(sampling_data_dir, f))
        filesize = ""
        if getsize <= 1000:
            # バイト表示
            filesize = "%s %s" % (str(getsize), "Byte") 
        else:
            if getsize <= 1000000:
                # Kバイト表示
                filesize = "%s %s" % (str(int(getsize / 1000)), "KB") 
            else:
                # Mバイト表示
                filesize = "%s %s" % (str(int(getsize / 1000000)), "MB") 

        ret.append([f, filesize])
    return ret


def reduced_power_consumption():
    """ 消費電力削減のため、HDMIの電源を切る
        return Bool
    """
    try:
        cmd = "/opt/vc/bin/tvservice --off"
        print(cmd)
        os.system(cmd)

        return True
    except:
        return False


#! /usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
#-----------------------------------------------------------------------
#   BME280（温度、湿度、気圧センサ）制御
#   bme280.py
#   https://www.switch-science.com/catalog/2236/
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
class Bme280(object):

    def __init__(self, sampling_proc):
        self.proc = sampling_proc
        self.cmd = "python %s" % self.proc


    def is_working(self):
        """ BME280が動いていてデータが取れる状態か確認する
        """
        res = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                shell=True).stdout.readlines()
        if len(res) == 0:
            return False
        return True


    def do_sampling(self, filename):
        """ データを取得しファイルに書き込む
        """
        res = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                shell=True).stdout.readlines()

        # データが取れなくてもファイルは作る
        with open(filename, "wt") as fd:
            for item in res:
                # asciiに変換できるものだけ書き込む
                line = ""
                try:
                    line = item.decode("ascii")
                except:
                    continue
                fd.writelines(line)
        return True


    def get_data(self):
        """
            return list(of String) 
            [] | [hum, press, temp]
        """
        res = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                shell=True).stdout.readlines()
        if len(res) == 0:
            return []
        # asciiに変換できるものだけ書き込む
        line = ""
        try:
            line = res[0].decode("ascii")
            items = line.split(",")
            ret = []
            for item in items:
                ret.append(float(item.replace('\n',"")))
            return ret
        except:
            return []
        return res

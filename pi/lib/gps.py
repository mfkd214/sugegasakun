#! /usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
#-----------------------------------------------------------------------
#   GPS制御
#   gps.py
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
class Gps(object):

    def __init__(self, port):
        self.port = port


    def is_working(self):
        """ Gpsが動いていてデータが取れる状態か確認する
        """
        cmd = "timeout 2 cat %s" % self.port
        res = subprocess.Popen(
                cmd, stdout=subprocess.PIPE,
                    shell=True).stdout.readlines()
        if len(res) == 0:
            return False
        return True


    def is_get_location(self, timeout=3):
        """ ロケーション情報が取得できるか確認
        """
        res = self.get_location(timeout)
        if len(res) == 0:
            return False
        return True


    def _sampling_command(self, timeout=3):
        return "timeout %s cat %s | grep -e GPRMC -e GPGGA" % \
                (timeout, self.port)


    def do_sampling(self, filename, timeout=3):
        """ GPRMCとGPGGAセンテンスだけを取得しファイルに書き込む
        """
        res = subprocess.Popen(
                self._sampling_command(timeout),
                stdout=subprocess.PIPE,
                shell=True).stdout.readlines()

        # センテンスが取れなくてもファイルは作る
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


    def _convert_location(self, dddmm_mmmm):
        """ 緯度や経度を一般的なものに変換する
        """
        lst = dddmm_mmmm.split(".")
        if len(lst) <= 1:
            return 0 

        lst[0] = lst[0].rjust(5, "0")
        lst[1] = lst[1].rjust(4, "0")
        
        d = lst[0][0:3]
        m = lst[0][3:] + "." + lst[1]

        try:
            ret = int(d) + float(m) / 60
            return ret 
        except:
            return 0


    def get_location(self, timeout=3):
        """ GPRMCとGPGGAセンテンスから緯度、経度、高度を返す
            但し、高度はオプションとし取得できない場合は""
            return list(of String) 
                [] | [let, lat, alt(option))
        """
        ret = list()
        res = subprocess.Popen(
                self._sampling_command(timeout),
                stdout=subprocess.PIPE,
                shell=True).stdout.readlines()

        ido = ""
        keido = ""
        koudo = ""
        for r in res:
            # asciiに変換できるものだけ使用する
            items = list()
            try:
                line = r.decode("ascii")
                items = line.split(",")
                if len(items) == 0:
                    continue
            except:
                continue

            # location取得
            if items[0].find("GPRMC") >= 0:
                if len(items) < 6:
                    continue

                tmp = self._convert_location(items[3])
                if tmp == 0:
                    continue
                ido = "%3.5f" % tmp

                tmp = self._convert_location(items[5])
                if tmp == 0:
                    continue
                keido = "%3.5f" % tmp

            elif items[0].find("GPGGA") >= 0:
                try:
                    koudo = str(float(items[9]))
                except:
                    continue
            else:
                continue

        if ido != "" and keido != "":
            ret.append(ido)
            ret.append(keido)
            ret.append(koudo)

        return ret


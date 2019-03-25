#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

class Gpsfile(object):

    def __init__(self, filename):
        """
        """
        self.filename = filename
        self.records = list()
        self.jst = None
        self.ido   = 0.0
        self.keido = 0.0
        self.koudo = 0.0

        self._include_gpsfile()


    def _convert_location(self, dddmm_mmmm):
        """
        """
        lst = dddmm_mmmm.split(".")

        lst[0] = lst[0].rjust(5, "0")
        lst[1] = lst[1].rjust(4, "0")
        
        d = lst[0][0:3]
        m = lst[0][3:] + "." + lst[1]

        return int(d) + float(m) / 60


    def _convert_jst(self, ddmmyy, hhmiss):
        """
        """
        d = datetime( \
                        int("20" + ddmmyy[4:6]),
                        int(ddmmyy[2:4]),
                        int(ddmmyy[0:2]),
                        int(hhmiss[0:2]),
                        int(hhmiss[2:4]),
                        int(hhmiss[4:6]))
        return d + timedelta(hours=9)


    def _expand_property(self):
        """
        """
        # 日時
        tmp_date = ""
        tmp_time = ""
        for record in self.records:
            if record[0] == "$GPRMC":
                if record[9] != "":
                    tmp_date = record[9]
                if record[1] != "":
                    tmp_time = record[1].split(".")[0]
            elif record[0] == "$GPGGA":
                if record[1] != "":
                    tmp_time = record[1].split(".")[0]
            else:
                continue

        if tmp_date == "" or tmp_time == "":
            return 1
        self.jst = self._convert_jst(tmp_date, tmp_time)

        # 緯度、経度、高度(Option)
        tmp_ido = ""
        tmp_keido = ""
        tmp_koudo = ""
        for record in self.records:
            if record[0] == "$GPRMC":
                if record[3] != "":
                    tmp_ido = record[3]
                if record[5] != "":
                    tmp_keido = record[5]
            elif record[0] == "$GPGGA":
                if record[2] != "":
                    tmp_ido = record[2]
                if record[4] != "":
                    tmp_keido = record[4]
                if record[9] != "":
                    tmp_koudo = record[9]
            else:
                continue
        if tmp_ido == "" or tmp_keido == "":
            return 1

        self.ido = self._convert_location(tmp_ido)
        self.keido = self._convert_location(tmp_keido)
        if tmp_koudo != "":
            self.koudo = float(tmp_koudo)

        return 0


    def _include_gpsfile(self):
        """
        """
        # ファイルがない場合、異常終了
        if not os.path.exists(self.filename):
            print("file is not found:", self.filename)
            return 4

        # 取込開始
        rtncd = 0
        readcnt = 0
        with open(self.filename, "rb") as f:

            for record in f:
                readcnt += 1

                # utf-8エンコードできないものはスキップ
                ascii_record    =   ""
                try:
                    ascii_record    =   record.decode("ascii")
                    ascii_record    =   ascii_record.replace("\r", "")
                    ascii_record    =   ascii_record.replace("\n", "")
                except:
                    print("encode error:", self.filename, record)
                    continue
                
                # カラム展開
                columns = ascii_record.split(",")
                if len(columns) == 0:
                    print("skip:", self.filename, record)
                    continue
                if columns[0] == "$GPRMC" and len(columns) == 13:
                    pass
                elif columns[0] == "$GPGGA" and len(columns) == 15:
                    pass
                else:
                    print("skip:", self.filename, record)
                    continue
                self.records.append(columns)

        if readcnt == 0:
            print("valid data nothing:", self.filename)
            return 1

        if self._expand_property() != 0:
            print("not expand property:", self.filename)
            return 1

        return rtncd

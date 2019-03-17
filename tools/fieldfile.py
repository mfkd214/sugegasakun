#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

class Fieldfile(object):

    def __init__(self, filename):
        """
        """
        self.filename = filename
        self.records = list()
        self.shitsudo = 0.0
        self.kiatsu   = 0.0
        self.ondo     = 0.0

        self._include_fieldfile()

    def _include_fieldfile(self):
        """
        """
        # ファイルがない場合、異常終了
        if not os.path.exists(self.filename):
            print("file is not found:", self.filename)
            return 4

        # 取込開始
        rtncd = 0
        readcnt = 0
        shitsudo_lst = list()
        kiatsu_lst   = list()
        ondo_lst     = list()
        with open(self.filename, "rb") as f:

            for record in f:
                readcnt += 1
                
                # utf-8エンコードできないものはスキップ
                ascii_record    =   ""
                try:
                    ascii_record    =   record.decode("ascii")
                    ascii_record    =   ascii_record.replace("\r", "")
                    ascii_record    =   ascii_record.replace("\n", "")
                except Exception:
                    print("encode error:", record)
                    continue

                # カラム展開
                columns = ascii_record.split(",")
                if len(columns) == 0:
                    print("skip:", record)
                    continue
                if len(columns) > 0:
                    shitsudo_lst.append(float(columns[0]))
                if len(columns) > 1:
                    kiatsu_lst.append(float(columns[1]))
                if len(columns) > 2:
                    ondo_lst.append(float(columns[2]))

        avg_ondo     = 0.0
        avg_shitsudo = 0.0
        avg_kiatsu   = 0.0
        if len(ondo_lst) > 0:
            avg_ondo = sum(ondo_lst) / len(ondo_lst)
        if len(shitsudo_lst) > 0:
            avg_shitsudo = sum(shitsudo_lst) / len(shitsudo_lst)
        if len(kiatsu_lst) > 0:
            avg_kiatsu = sum(kiatsu_lst) / len(kiatsu_lst)

        self.shitsudo = avg_shitsudo
        self.kiatsu   = avg_kiatsu
        self.ondo     = avg_ondo

        if readcnt == 0:
            return 1           

        return rtncd

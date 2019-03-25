#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os

class Luxfile(object):

    def __init__(self, filename):
        """
        """
        self.filename = filename
        self.records = list()
        self.lux  = 0.0
        self.full = 0.0
        self.ir   = 0.0

        self._include_file()

    def _include_file(self):
        """
        """
        # ファイルがない場合、異常終了
        if not os.path.exists(self.filename):
            print("file is not found:", self.filename)
            return 4

        # 取込開始
        rtncd = 0
        readcnt = 0
        lux_lst = list()
        full_lst = list()
        ir_lst = list()
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
                    lux_lst.append(float(columns[0]))
                if len(columns) > 1:
                    full_lst.append(float(columns[1]))
                if len(columns) > 2:
                    ir_lst.append(float(columns[2]))

        avg_lux = 0.0
        avg_full = 0.0
        avg_ir = 0.0
        if len(lux_lst) > 0:
            avg_lux = sum(lux_lst) / len(lux_lst)
        if len(full_lst) > 0:
            avg_full = sum(full_lst) / len(full_lst)
        if len(ir_lst) > 0:
            avg_ir = sum(ir_lst) / len(ir_lst)

        self.lux = avg_lux
        self.full = avg_full
        self.ir = avg_ir

        if readcnt == 0:
            return 1           

        return rtncd

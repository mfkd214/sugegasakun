#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import SI1145.SI1145 as SI1145
#-----------------------------------------------------------------------
#   SI1145@i2c制御
#   sampling_si1145.py
#
#   UV Index等を採取し、標準出力に出力する
#   元ネタ：https://github.com/THP-JOE/Python_SI1145
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
if __name__ == '__main__':
    try:
        sensor = SI1145.SI1145()
        vis = sensor.readVisible()
        ir = sensor.readIR()

        uv = sensor.readUV()
        uv_index = uv / 100.0

        print "%s,%s,%s" % (uv_index, vis, ir)
        exit(0)
    except:
        exit(4)

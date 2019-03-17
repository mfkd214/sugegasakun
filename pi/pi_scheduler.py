#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import datetime

import config
from lib import myutils, camera, gps, bme280, si1145, tsl2591
#-----------------------------------------------------------------------
#   菅笠くん on RaspberryPI
#   pi_scheduler.py
#
#   菅笠くん on RaspberryPIのデータ保存サービス(cron起動)
#
#   1.0.0   mfkd    Created
#-----------------------------------------------------------------------
SCHEDULER_FILE = config.SCHEDULER_FILE
CAM_KICK_SH = config.CAM_KICK_SH
STREAM_URL = config.STREAM_URL
SER_PORT = config.SER_PORT
BME280_SAMP = config.BME280_SAMP
SI1145_SAMP = config.SI1145_SAMP
TSL2591_SAMP = config.TSL2591_SAMP
SAMPLING_DATA_DIR = config.SAMPLING_DATA_DIR

_cam = camera.Camera(CAM_KICK_SH, STREAM_URL)
_gps = gps.Gps(SER_PORT)
_bme = bme280.Bme280(BME280_SAMP)
_si = si1145.Si1145(SI1145_SAMP)
_tsl = tsl2591.Tsl2591(TSL2591_SAMP)

# スケジューラoffの場合、実行しない
#-----------------------------
if not (myutils.is_scheduler_working(SCHEDULER_FILE)):
    print("schedule OFF")
    exit(1)

# サンプリング開始
#---------------
#-- HDMIの電源を切る
#myutils.reduced_power_consumption()

now = datetime.datetime.now()
filename = now.strftime('%Y%m%d%H%M%S')
path = ""

#-- 写真は２枚
for i in range(2):
    path = "%s%d.jpg" % \
            (os.path.join(SAMPLING_DATA_DIR, filename), i + 1) 
    if not (_cam.do_snap(path)):
        print("Camera do_snap Error")
        
#-- GPS
path = "%s.gps.txt" % os.path.join(SAMPLING_DATA_DIR, filename) 
if not (_gps.do_sampling(path)):
    print("GPS do_sampling Error")

#-- BME280
path = "%s.field.txt" % os.path.join(SAMPLING_DATA_DIR, filename) 
if not (_bme.do_sampling(path)):
    print("BME280 do_sampling Error")

#-- SI1145
path = "%s.uvindex.txt" % os.path.join(SAMPLING_DATA_DIR, filename) 
if not(_si.do_sampling(path)):
    print("SI1145 do_sampling Error")

#-- TSL2591
path = "%s.lux.txt" % os.path.join(SAMPLING_DATA_DIR, filename) 
if not(_tsl.do_sampling(path)):
    print("TSL2591 do_sampling Error")

exit(0)

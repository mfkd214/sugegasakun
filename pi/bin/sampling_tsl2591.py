#!/usr/bin/python
# -*- coding: utf-8 -*-
import tsl2591

#-----------------------------------------------------------------------
#   TSL2591@i2c制御
#   sampling_tsl2591.py
#
#   照度(lux)等を採取し、標準出力に出力する
#   元ネタ：https://github.com/maxlklaxl/python-tsl2591
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
if __name__ == '__main__':
    try:
	# initialize
        tsl = tsl2591.Tsl2591()

        # read raw values (full spectrum and ir spectrum)
        full, ir = tsl.get_full_luminosity()

        # convert raw values to lux
        lux = tsl.calculate_lux(full, ir)  

        print "%s,%s,%s" % (lux, full, ir)

        exit(0)
    except:
        exit(4)




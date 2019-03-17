#!/usr/bin/python
# -*- coding: utf-8 -*-
from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus
from time import sleep
#-----------------------------------------------------------------------
#   APDS9960@i2c制御
#   sampling_apds9960.py
#
#   RGB、AmbientLight(環境光)を採取し、標準出力に出力する
#   元ネタ：https://github.com/liske/python-apds9960
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
if __name__ == '__main__':
    port = 1
    bus = smbus.SMBus(port)

    apds = APDS9960(bus)

    def intH(channel):
        print("INTERRUPT")

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.IN)
    try:
        # Interrupt-Event hinzufuegen, steigende Flanke
        GPIO.add_event_detect(7, GPIO.FALLING, callback = intH)

        print("Light Sensor Test")
        print("=================")
        apds.enableLightSensor()
        oval = -1
        while True:
            sleep(0.25)

            val = apds.readAmbientLight()
            if val != oval:
                oval = val

            sleep(0.25)
            r = apds.readRedLight()

            sleep(0.25)
            g = apds.readGreenLight()

            sleep(0.25)
            b = apds.readBlueLight()

            print("Ambient:%d Red:%d Green:%d Blue:%d" % (
                        val, r, g, b))

    finally:
        GPIO.cleanup()
        print "Bye"

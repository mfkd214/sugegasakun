#! /usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import tornado.ioloop
import tornado.web

import config
from lib import myutils, camera, gps, bme280, si1145, tsl2591
#-----------------------------------------------------------------------
#   菅笠くん on RaspberryPI
#   pi_index.py
#
#   菅笠くん on RaspberryPIのWEBサービス
#
#   1.0.0               mfkd    Created
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

class IndexHandler(tornado.web.RequestHandler):
    """ /

    """
    def get(self):
        self.render(
                "index.html",
                server_now = myutils.get_sysdate_string())

    def post(self):
        
        val = self.get_arguments("client_now")[0]
        if val != "":
            myutils.set_clock(val)

        self.redirect("/main")



class MainHandler(tornado.web.RequestHandler):
    """ メインページ
    """
    def get(self):
        self.render(
                "main.html",
                server_datetime = myutils.get_formated_sysdate(),
                scheduler_status =
                    myutils.get_scheduler_status(SCHEDULER_FILE),
                streamer_status = myutils.bool2str(
                                    _cam.is_streamer_working()),
                camera_status = myutils.bool2str(
                                    _cam.is_camera_working()),
                gps_status = myutils.bool2str(_gps.is_working()),
                gps_location_status = myutils.bool2str(
                                        _gps.is_get_location()),
                bme280_status = myutils.bool2str(_bme.is_working()),
                si1145_status = myutils.bool2str(_si.is_working()),
                tsl2591_status = myutils.bool2str(_tsl.is_working()),
        )

    def post(self):
        mode = self.get_arguments("mode")
        if len(mode) > 0:
            if mode[0] == "1":
                # スケジューラ切替
                myutils.change_scheduler_status(SCHEDULER_FILE)

            elif mode[0] == "9":
                # シャットダウン
                myutils.shutdown()


        self.redirect("/")



class CameraHandler(tornado.web.RequestHandler):
    """ カメラページ
    """
    def get(self):
        self.render(
                "camera.html",
                stream_url = _cam.stream_url,
        )

    def post(self):
        mode = self.get_arguments("mode")
        if len(mode) > 0:
            if mode[0] == "1":
                # 撮影等
                for i in range(2):
                    now =   datetime.datetime.now()
                    filename = now.strftime('%Y%m%d%H%M%S')
                    _cam.do_snap(
                        "%s.jpg" % os.path.join(SAMPLING_DATA_DIR, filename))
                    _gps.do_sampling(
                        "%s.gps.txt" % os.path.join(SAMPLING_DATA_DIR, filename))
                    _bme.do_sampling(
                        "%s.field.txt" % os.path.join(SAMPLING_DATA_DIR, filename))
                    _si.do_sampling(
                        "%s.uvindex.txt" % os.path.join(SAMPLING_DATA_DIR, filename))
                    _tsl.do_sampling(
                        "%s.lux.txt" % os.path.join(SAMPLING_DATA_DIR, filename))
                    
            elif mode[0] == "2":
                # 再起動
                _cam.streamer_restart()
            else:
                pass
        self.redirect("/camera")


class SensorHandler(tornado.web.RequestHandler):
    """ センサーページ
    """
    def get(self):
        # GPS
        gps_ido = "-"
        gps_keido = "-"
        gps_koudo = "-"
        gps_is_working = _gps.is_working()
        gps_is_get_location = _gps.is_get_location()
        if gps_is_get_location:
            get_location = _gps.get_location()
            if len(get_location) == 3:
                gps_ido = get_location[0]
                gps_keido = get_location[1]
                gps_koudo = get_location[2]
            print("GPS:", get_location)

        # BME280
        bme_temp = ""
        bme_hum = ""
        bme_press = ""
        bme_alt = ""
        bme_is_working = _bme.is_working()
        if bme_is_working:
            get_data = _bme.get_data()
            if len(get_data) == 3:
                bme_hum = "%s %s" % (str(get_data[0]), "%")
                bme_press = "%s hpa" % str(get_data[1])
                bme_temp = "%s ℃" % str(get_data[2])
            print("BME:", get_data)

        # SI1145
        si_uvindex = ""
        si_vis = ""
        si_ir = ""
        si_is_working = _si.is_working()
        if si_is_working:
            get_data = _si.get_data()
            if len(get_data) == 3:
                si_uvindex = str(get_data[0])
                si_vis = str(get_data[1])
                si_ir = str(get_data[2])
            print("SI:", get_data)

        # TSL2591
        tsl_lux = ""
        tsl_full = ""
        tsl_ir = ""
        tsl_is_working = _tsl.is_working()
        if tsl_is_working:
            get_data = _tsl.get_data()
            if len(get_data) == 3:
                tsl_lux = str(get_data[0])
                tsl_full = str(get_data[1])
                tsl_ir = str(get_data[2])
            print("TSL:", get_data)

        self.render(
                "sensor.html",
                server_now = myutils.get_formated_sysdate(),
                gps_status = myutils.bool2str(gps_is_working),
                gps_location_status = myutils.bool2str(
                                        gps_is_get_location),
                gps_ido = gps_ido,
                gps_keido = gps_keido,
                gps_koudo =  gps_koudo,
                bme_status = myutils.bool2str(bme_is_working),
                bme_temp = bme_temp,
                bme_hum = bme_hum,
                bme_press = bme_press,
                bme_alt = bme_alt,
                si_status = myutils.bool2str(si_is_working),
                si_uvindex = si_uvindex,
                si_vis = si_vis,
                si_ir = si_ir,
                tsl_status = myutils.bool2str(tsl_is_working),
                tsl_lux = tsl_lux,
                tsl_full = tsl_full,
                tsl_ir = tsl_ir,
        )


class SamplingLogHandler(tornado.web.RequestHandler):
    """ サンプリングファイル一覧ページ
    """
    def get(self):
        logs = myutils.get_sampling_log(SAMPLING_DATA_DIR)
        if len(logs) == 0:
            logs.append(["該当データなし", ""])
        self.render(
                "log.html",
                server_datetime = myutils.get_formated_sysdate(),
                data_dir = SAMPLING_DATA_DIR,
                logs = logs,
        )



if __name__ == "__main__":
    import sys
    import os
    def make_app():
        return tornado.web.Application([
            (r"/", IndexHandler),
            (r"/main", MainHandler),
            (r"/camera", CameraHandler),
            (r"/sensor", SensorHandler),
            (r"/log", SamplingLogHandler),
            ],
            template_path=os.path.join(os.getcwd(), "templates"),
            static_path=os.path.join(os.getcwd(),   "static"))

    port = 8000
    argv = sys.argv
    if len(argv) > 1:
        port = int(argv[1])

    app = make_app()
    app.listen(port)

    tornado.ioloop.IOLoop.current().start()

#! /usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import subprocess
import time
#-----------------------------------------------------------------------
#   mjpg_streamerを使用したカメラ制御
#   camera.py
#
#   1.0.0               mfkd    Created
#-----------------------------------------------------------------------
class Camera(object):

    def __init__(self, ctrl_sh, server_url):
        """ コンストラクタ
        """
        self.ctrl_sh = ctrl_sh
        self.url = server_url
        self.stream_url = "%s/?action=stream" % server_url
        self.snapshot_url = "%s/?action=snapshot" % server_url


    def streamer_start(self):
        """ mjpg_streamerを起動する
        """
        cmd = "%s %s" % (self.ctrl_sh, "start")
        subprocess.call(cmd, shell=True)

        return self.is_streamer_working()


    def streamer_stop(self):
        """ mjpg_streamerを停止する
        """
        cmd = "%s %s" % (self.ctrl_sh, "stop")
        subprocess.call(cmd, shell=True)

        return not self.is_streamer_working()


    def is_streamer_working(self):
        """ mjpg_streamerが動いているか確認する
        """
        keyword = "mjpg_streamer"
        cmd = "ps ax | grep " + keyword + " | grep -v grep | wc -l"
        try:
            # result should be proess count string
            result = subprocess.check_output(
                        cmd, shell=True).decode("utf-8").strip()
            if result != "0":
                return True
            return False
        except Exception as e:
            return False


    def streamer_restart(self):
        """ 再起動する
        """
        self.streamer_stop()
        self.streamer_start()
        time.sleep(3)
        return self.is_streamer_working()


    def is_camera_working(self):
        """ 写真が撮れる状態か確認する
        """
        try:
            timeout = 3
            res = requests.get(
                        self.snapshot_url,
                        allow_redirects=False,
                        timeout=timeout)
            if res.status_code != 200:
                return False
            return True
        except Exception as e:
            return False


    def do_snap(self, filename):
        """ 撮影する
        """
        try:
            timeout = 3
            res = requests.get(
                        self.snapshot_url,
                        allow_redirects=False,
                        timeout=timeout)
            if res.status_code != 200:
                return False

            with open(filename, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            return False

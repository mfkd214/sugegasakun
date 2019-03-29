#! /usr/bin/python3
# -*- coding: utf-8 -*-

class Summary(object):

    def __init__(self, ymd):
        self.gps_ymd = ymd
        self.rows = list()
        self.start_time = ""
        self.ended_time = ""
        self.ondos = list()
        self.shitsudos = list()
        self.kiatsus = list()
        self.uvindexes = list()
        self.luxes = list()
        self.koudos = list()


    def stack(self, rec):

        # 時刻
        if len(self.rows) == 0:
            self.start_time = rec["gpsdate"][11:16]
        self.ended_time = rec["gpsdate"][11:16]

        # 気温スタック
        if rec["ondo"] > 0:
            self.ondos.append(rec["ondo"])

        # 湿度スタック
        if rec["shitsudo"] > 0:
            self.shitsudos.append(rec["shitsudo"])

        # 気圧スタック
        if rec["kiatsu"] > 0:
            self.kiatsus.append(rec["kiatsu"])

        # UVINDEXスタック
        if rec["uvindex"] > 0:
            self.uvindexes.append(rec["uvindex"])

        # 照度スタック
        if rec["lux"] > 0:
            self.luxes.append(rec["lux"])

        # 高度スタック
        if rec["koudo"] > 0:
            self.koudos.append(rec["koudo"])

        # レコードスタック
        self.rows.append(rec)


    def _get_avg(self, ilist):
        ret = 0.0
        if len(ilist) > 0:
            ret = sum(ilist) / len(ilist)
        return ret


    def _get_min(self, ilist):
        if len(ilist) > 0:
            l = sorted(ilist)
            return l[0]
        else:
            return 0.0


    def _get_max(self, ilist):
        if len(ilist) > 0:
            l = sorted(ilist,reverse=True)
            return l[0]
        else:
            return 0.0


    def avgondo_per_day(self):
        return self._get_avg(self.ondos)


    def minondo_per_day(self):
        return self._get_min(self.ondos)


    def maxondo_per_day(self):
        return self._get_max(self.ondos)

                
    def avgshitsudo_per_day(self):
        return self._get_avg(self.shitsudos)


    def minshitsudo_per_day(self):
        return self._get_min(self.shitsudos)


    def maxshitsudo_per_day(self):
        return self._get_max(self.shitsudos)


    def avgkiatsu_per_day(self):
        return self._get_avg(self.kiatsus)


    def minkiatsu_per_day(self):
        return self._get_min(self.kiatsus)


    def maxkiatsu_per_day(self):
        return self._get_max(self.kiatsus)


    def avguvindex_per_day(self):
        return self._get_avg(self.uvindexes)


    def minuvindex_per_day(self):
        return self._get_min(self.uvindexes)


    def maxuvindex_per_day(self):
        return self._get_max(self.uvindexes)


    def avglux_per_day(self):
        return self._get_avg(self.luxes)


    def minlux_per_day(self):
        return self._get_min(self.luxes)


    def maxlux_per_day(self):
        return self._get_max(self.luxes)


    def minkoudo_per_day(self):
        return self._get_min(self.koudos)


    def maxkoudo_per_day(self):
        return self._get_max(self.koudos)


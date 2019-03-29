#! /usr/bin/python3
# -*- coding: utf-8 -*-
import googlemaps
import lib.config as config

class Gmaps(object):

    def __init__(self):

        self.gmaps = googlemaps.Client(config.GMAP_APIKEY)


    def location_name(self, ido, keido):
        """ 場所名取得
        """
        res = self.gmaps.reverse_geocode(
                                (ido, keido),
                                language="ja",
                                result_type="locality|sublocality",
                                location_type="APPROXIMATE")
        if len(res) > 0:
            return res[0]["formatted_address"]
        else:
            print(ido, keido)
            return "不明"

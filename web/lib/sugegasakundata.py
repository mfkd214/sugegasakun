#! /usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

def _connect_time(datetime_from, datetime_to):
    return "%s〜%s" % (datetime_from[11:], datetime_to[11:])

def _format_basho_nm(basho_nm):
    l = basho_nm.split(" ")
    if len(l) > 1:
        return l[1]
    l = l[0].split("、")
    if len(l) > 1:
        return l[1]
    return l[0]

def _generate_key(datetime_from, datetime_to):
    return "%s%s" % \
        (datetime_from.replace("-", "").replace(" ", "").replace(":", ""),
         datetime_to.replace("-", "").replace(" ", "").replace(":", ""))

def _generate_from_to(iYmd, iRange):
    base = datetime(int(iYmd[0:4]), int(iYmd[4:6]), int(iYmd[6:8]), 0,0,0)
    prv  = base - timedelta(days=iRange)
    nxt  = base + timedelta(days=iRange)
    return prv.strftime("%m-%d"), nxt.strftime("%m-%d")

def _parse_key_datetime(iDate):
    return "%s-%s-%s %s:%s:%s" % ( \
                iDate[:4],   iDate[4:6],   iDate[6:8],
                iDate[8:10], iDate[10:12], iDate[12:14])

def _parse_key_from_to(iKey):
    fr = _parse_key_datetime(iKey[:14])
    to = _parse_key_datetime(iKey[14:])
    return fr, to

def _add_minuites(iDatetime, iMinuites):
    dt = datetime.strptime(iDatetime, "%Y-%m-%d %H:%M:%S")
    nxt = dt + timedelta(minutes=iMinuites)
    return nxt.strftime("%Y-%m-%d %H:%M:%S")

def _generate_limittime(iYmdhms, iRange, flg):
    """
    """
    base = datetime(
            int(iYmdhms[0:4]), int(iYmdhms[5:7]), int(iYmdhms[8:10]),
            int(iYmdhms[11:13]), int(iYmdhms[14:16]), int(iYmdhms[17:]))
    nxt  = base + timedelta(minutes=iRange)
    if flg == 0:
        if nxt.minute <= 30:
            nxt = datetime(nxt.year, nxt.month, nxt.day,
                           nxt.hour, 0, 0)
        else:
            nxt = datetime(nxt.year, nxt.month, nxt.day,
                           nxt.hour, 30, 1)
    print(nxt)
    return nxt.strftime("%Y-%m-%d %H:%M:%S")

    
class SugegasakunData(object):

    def __init__(self, iDb):

        self.db = iDb


    def search_of_month(self, iMonth, iKeyword):
        """
        """
        iMonth = iMonth.zfill(2)
        for r in self.db.fill_summary_of_month(
                                iMonth, iKeyword):
            yield (r[0],
                   _connect_time(r[1], r[2]),
                   _format_basho_nm(r[3]),
                   r[4],
                   "%3.1f" % r[5],
                   "%3.2f" % r[6],
                   "%4.2f" % r[7],
                   _generate_key(r[1], r[2]),)


    def search_of_range(self, iKey, iDayRange, iKeyword):
        """
        """
        results = list()
        month = ""

        md_fr, md_to = _generate_from_to(iKey, iDayRange)
        for r in self.db.fill_summary_of_md_range(
                                md_fr, md_to, iKeyword):
            if month == "":
                month = r[0][5:7]

            results.append( \
                  (r[0],
                   _connect_time(r[1], r[2]),
                   _format_basho_nm(r[3]),
                   r[4],
                   "%3.1f" % r[5],
                   "%3.1f" % r[6],
                   "%4.2f" % r[7],
                   _generate_key(r[1], r[2]),))

        return month, results


    def _get_sumaries(self, iFrom):
        date_range = ""
        basho_nm = ""
        avg_ondo = 0.0
        avg_shitsudo = 0.0
        avg_kiatsu = 0.0        
        for r in self.db.fill_summary_of_gpsdate_from(iFrom):
            basho_nm = "%s(%sm)" % (_format_basho_nm(r[3]), r[4])
            date_range = "%s %s" % (r[0], _connect_time(r[1], r[2]))
            avg_ondo = r[5]
            avg_shitsudo = r[6]
            avg_kiatsu = r[7]

        return date_range, basho_nm, avg_ondo, avg_shitsudo, avg_kiatsu


    def _get_mapdata_details(self, iFrom, iTo):
        # map location
        location = ""
        max_koudo = 0.0
        min_koudo = 999.9
        max_ondo = 0.0
        min_ondo = 999.9
        max_shitsudo = 0.0
        min_shitsudo = 999.9
        max_kiatsu = 0.0
        min_kiatsu = 9999.9
        detail_results = list()
        for r in self.db.fill_gps_gpsdate_range(iFrom, iTo):

            detail_results.append([ \
                r[1],
                "%4.1f" % r[4],
                "%3.1f" % r[5],
                "%3.2f" % r[6],
                "%4.2f" %  r[7]])

            ido = r[2]
            keido = r[3]

            # 最高、最低高度
            if r[4] > max_koudo:
                max_koudo = r[4]
            if r[4] > 0 and r[4] < min_koudo:
                min_koudo = r[4]
            # 最高、最低気温
            if r[5] > max_ondo:
                max_ondo = r[5]
            if r[5] > 0 and r[5] < min_ondo:
                min_ondo = r[5]
            # 最高、最低気温
            if r[6] > max_shitsudo:
                max_shitsudo = r[6]
            if r[6] > 0 and r[6] < min_shitsudo:
                min_shitsudo = r[6]
            # 最高、最低気圧
            if r[7] > max_kiatsu:
                max_kiatsu = r[7]
            if r[7] > 0 and r[7] < min_kiatsu:
                min_kiatsu = r[7]

            if location == "":
                location += "|{0},{1}".format(r[2], r[3])
                limit_datetime = _add_minuites(r[1], 10)
                continue

            if limit_datetime < r[1]:
                location += "|{0},{1}".format(r[2], r[3])
                limit_datetime = _add_minuites(limit_datetime, 10)
                continue
        location += "|{0},{1}".format(ido, keido)

        return location, max_koudo, min_koudo, max_ondo, min_ondo, \
                max_shitsudo, min_shitsudo, max_kiatsu, min_kiatsu, \
                detail_results


    def get_map_details_data(self, iKey):
        """
        <args>
            iKey: 2017050110041020170501134414
        <return>
        ex) location: ret += "|{0},{1}".format(ido, keido)
            ondo, shitsudo: [(14:00, 14:10, 99.9),...]
            kiatsu: [(14:00, 14:10, 9999.99),...]
            koudo: [(14:00, 14:10, 9999.99),...]
        """

        fr, to = _parse_key_from_to(iKey)

        # summary
        date_range, basho_nm, avg_ondo, avg_shitsudo, avg_kiatsu = \
            self._get_sumaries(fr)

        # map location
        location, max_koudo, min_koudo, max_ondo, min_ondo, \
         max_shitsudo, min_shitsudo, max_kiatsu, min_kiatsu, \
          detail_results = self._get_mapdata_details(fr, to)

        # return format
        summary_results = list()
        summary_results.append(["気温", "%3.1f" % avg_ondo,
                                       "%3.1f" % min_ondo,
                                       "%3.1f" % max_ondo])
        summary_results.append(["湿度", "%3.2f" % avg_shitsudo,
                                       "%3.2f" % min_shitsudo,
                                       "%3.2f" % max_shitsudo])
        summary_results.append(["気圧", "%4.2f" % avg_kiatsu,
                                       "%4.2f" % min_kiatsu,
                                       "%4.2f" % max_kiatsu])
        summary_results.append(["標高", "-",
                                       "%4.1f" % min_koudo,
                                       "%4.1f" % max_koudo])

        return date_range[5:7], date_range, basho_nm, summary_results, \
                location, detail_results


    def get_map_graph_data(self, iKey):
        """
        <args>
            iKey: 2017050110041020170501134414
        <return>
        ex) location: ret += "|{0},{1}".format(ido, keido)
            ondo, shitsudo: [(14:00, 14:10, 99.9),...]
            kiatsu: [(14:00, 14:10, 9999.99),...]
            koudo: [(14:00, 14:10, 9999.99),...]
        """

        fr, to = _parse_key_from_to(iKey)

        # summary
        date_range, basho_nm, avg_ondo, avg_shitsudo, avg_kiatsu = \
            self._get_sumaries(fr)

        # map location
        location, max_koudo, min_koudo, max_ondo, min_ondo, \
         max_shitsudo, min_shitsudo, max_kiatsu, min_kiatsu, \
          detail_results = self._get_mapdata_details(fr, to)

        # graph
        grp_koudo_data = list()
        grp_ondo_data = list()
        grp_shitsudo_data = list()
        grp_kiatsu_data = list()
        koudo = ""
        ondo = ""
        shitsudo = ""
        kiatsu = ""
        for i, result in enumerate(detail_results):
            if i == 0:
                grp_koudo_data.append([result[0][11:16], result[1]])
                grp_ondo_data.append([result[0][11:16], result[2]])
                grp_shitsudo_data.append([result[0][11:16], result[3]])
                grp_kiatsu_data.append([result[0][11:16], result[4]])
                limit_time = _generate_limittime(result[0], 30, 0)
                continue

            if result[0] > limit_time:
                grp_koudo_data.append([limit_time[11:16], koudo])
                grp_ondo_data.append([limit_time[11:16], ondo])
                grp_shitsudo_data.append([limit_time[11:16], shitsudo])
                grp_kiatsu_data.append([limit_time[11:16], kiatsu])
                limit_time = _generate_limittime(limit_time, 30, 1)
                continue

            ymdhms = result[0]
            koudo = result[1]
            ondo = result[2]
            shitsudo = result[3]
            kiatsu = result[4]

        grp_koudo_data.append([ymdhms[11:16], koudo])
        grp_ondo_data.append([ymdhms[11:16], ondo])
        grp_shitsudo_data.append([ymdhms[11:16], shitsudo])
        grp_kiatsu_data.append([ymdhms[11:16], kiatsu])
                
        summary_results = list()
        summary_results.append(["気温", "%3.1f" % avg_ondo,
                                       "%3.1f" % min_ondo,
                                       "%3.1f" % max_ondo])
        summary_results.append(["湿度", "%3.2f" % avg_shitsudo,
                                       "%3.2f" % min_shitsudo,
                                       "%3.2f" % max_shitsudo])
        summary_results.append(["気圧", "%4.2f" % avg_kiatsu,
                                       "%4.2f" % min_kiatsu,
                                       "%4.2f" % max_kiatsu])
        summary_results.append(["標高", "-",
                                       "%4.1f" % min_koudo,
                                       "%4.1f" % max_koudo])

        print(grp_koudo_data)
        print(grp_ondo_data)
        print(grp_shitsudo_data)
        print(grp_kiatsu_data)

        return date_range[5:7], date_range, basho_nm, \
                summary_results, location, grp_koudo_data, \
                 grp_ondo_data, grp_shitsudo_data, grp_kiatsu_data

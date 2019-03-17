#! /usr/bin/python3
# -*- coding: utf-8 -*-
import unittest
from gpsfile import Gpsfile
class TestCommunicate(unittest.TestCase):
    """ 疎通テスト
    """
    def setUp(self):
        self.gps = Gpsfile("/home/mfkd/repo/sugegasakun/tools/tests/20180331160601.gps.txt")
        #self.gps = Gpsfile("/home/mfkd/server/sugegasakun_data_unzip20170414112609.gps.txt")

    def test_initial(self):
        """
        """
        self.assertEqual(len(self.gps.records), 2)
        print(self.gps.records)

class TestError(unittest.TestCase):
    """ 疎通テスト
    """
    def setUp(self):
        self.gps = Gpsfile("/home/mfkd/repo/sugegasakun/tools/tests/gps.txt")

    def test_initial(self):
        """
        """
        self.assertEqual(len(self.gps.records), 0)
        print(self.gps.records)


if __name__ == '__main__':
    unittest.main()

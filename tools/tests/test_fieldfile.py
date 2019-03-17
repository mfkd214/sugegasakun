#! /usr/bin/python3
# -*- coding: utf-8 -*-
import unittest
from fieldfile import Fieldfile
class TestCommunicate(unittest.TestCase):
    """ 疎通テスト
    """
    def setUp(self):
        self.field = Fieldfile("/home/mfkd/repo/sugegasakun/tools/tests/20170414112609.field.txt")

    def test_initial(self):
        """
        """
        self.assertEqual(len(self.field.records), 5)
        print(self.field.records)

class TestError(unittest.TestCase):
    """ 疎通テスト
    """
    def setUp(self):
        self.field = Fieldfile("/home/mfkd/repo/sugegasakun/tools/tests/fiels.txt")

    def test_initial(self):
        """
        """
        self.assertEqual(len(self.field.records), 0)
        print(self.field.records)


if __name__ == '__main__':
    unittest.main()

import urllib2
import unittest

import fake_http_service
from feedhandlers.google import PRICE_URL, QUOTE_URL
from feedhandlers.yahoo import YAHOO_URL


_TEST_URL = "http://example.com/testfile.txt"
_TEST_YAHOO_URL = YAHOO_URL + 's=GOOG&f=sl1d1t1c1ohgv&e=.csv'


class FakeHttpServiceTest(unittest.TestCase):
    def test_simple_download(self):
        fake_http_service.install_file_http_handler()
        doc = urllib2.urlopen(_TEST_URL)
        self.assertEqual(doc.read(), "test data\n")


class FakeHttpDataServiceTest(unittest.TestCase):
    def setUp(self):
        fake_http_service.install_data_file_http_handler()

    def test_google_price_data_download(self):
        doc = urllib2.urlopen(
            PRICE_URL + 'q=GOOG&x=NASD&i=86400&p=40Y&f=d,c,v,k,o,h,l')
        content = doc.read()
        self.assertEqual(
            self._read_file('data/google/prices/GOOG.csv'), content)

    def test_google_quote_data_download(self):
        doc = urllib2.urlopen(QUOTE_URL + 'q=NASDAQ:GOOG')
        content = doc.read()
        self.assertEqual(
            self._read_file('data/google/quotes/NASDAQ:GOOG.json'), content)

    def test_yahoo_data_download(self):
        doc = urllib2.urlopen(_TEST_YAHOO_URL)
        content = doc.read()
        self.assertEqual(self._read_file('data/yahoo/GOOG.csv'), content)

    def _read_file(self, filename):
        with open(filename, 'r') as f:
            return f.read()

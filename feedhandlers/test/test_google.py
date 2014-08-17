import datetime as dt
import urllib2
import logging
from mock import patch
import pytz
import sys
import unittest

import fake_http_service
import feedhandlers.google as google


class TestGoogle(unittest.TestCase):

    def setUp(self):
        fake_http_service.install_data_file_http_handler()

    def test_build_timestamp_utc(self):
        timestamp_iso = '2014-07-16T16:00:01Z'
        date_ts = 'Jul 16, 4:00PM EDT'
        self.assertEqual(
            dt.datetime(2014, 7, 16, 20, 0, 1, 0, pytz.utc),
            google.QuoteResponse._build_timestamp_utc(date_ts, timestamp_iso))

    def test_request_quote_GOOG(self):
        quote_response = google.request_quote(['GOOG'])
        self.assertEqual(582.66, quote_response.last_price)
        self.assertEqual(dt.datetime(2014, 7, 16, 20, 0, 1, 0, pytz.utc),
                         quote_response.last_trade_time)

    def test_request_quote_ANZ(self):
        quote_response = google.request_quote(['ANZ'], 'ASX')
        self.assertEqual(33.31, quote_response.last_price)
        self.assertEqual(dt.datetime(2014, 7, 22, 22, 53, 45, 0, pytz.utc),
                         quote_response.last_trade_time)

    def test_request_daily_prices(self):
        expected_entries = 2495

        price_response = google.request_prices('GOOG', interval=86400)
        self.assertEqual(expected_entries, price_response.length)
        self.assertListEqual(
            [dt.datetime(2004, 8, 19, 20, 0),
             49.955, 51.978, 47.932, 50.117, 0],
            price_response.raw_data(0))
        self.assertListEqual(
            [dt.datetime(2014, 7, 18, 20, 0),
             593.0, 596.8, 582.0, 595.08, 4006389],
            price_response.raw_data(expected_entries - 1))

    def test_request_intraday_minute_prices(self):
        expected_entries = 499
        price_response = google.request_prices('BARC', exchange='LON',
                                               interval=60)
        self.assertEqual(expected_entries, price_response.length)
        self.assertListEqual(
            [dt.datetime(2014, 7, 25, 7, 1),
             214.95, 215.573, 214.65, 215.5, 694621.0],
            price_response.raw_data(0))
        self.assertListEqual(
            [dt.datetime(2014, 7, 25, 15, 30),
             218.4, 218.4, 218.15, 218.1995, 116648.0],
            price_response.raw_data(expected_entries - 1))

    def test_request_intraday_minute_prices(self):
        """CDATA field is not returned on all queries"""
        expected_entries = 458
        price_response = google.request_prices('AAL', exchange='LON',
                                               interval=60)
        self.assertEqual(expected_entries, price_response.length)
        self.assertListEqual(
            [dt.datetime(2014, 8, 06, 7, 0),
             1547.5, 1547.5, 1547.5, 1547.5, 15951.0],
            price_response.raw_data(0))
        self.assertListEqual(
            [dt.datetime(2014, 8, 6, 15, 29),
             1568.0, 1568.5, 1568.0, 1568.5, 2338.0],
            price_response.raw_data(expected_entries - 1))

    def test_create_option_chain_request(self):
        self.assertEqual(
            google.OPTIONS_CHAIN_URL.format('TEST'),
            google._create_option_request_url('TEST', None, None, None))

        self.assertEqual(
            google.OPTIONS_CHAIN_DATE_URL.format('TEST', 31, 12, 2014),
            google._create_option_request_url('TEST', 31, 12, 2014))

    def test_dummy_url_requests(self):
        with patch('feedhandlers.google._send_request') as gmock:
            google.dummy_request('TEST', 'EXCH', 0)
            gmock.assert_called_with(
                 google.DUMMY_URLS[0].format('EXCH%3ATEST'))

            google.dummy_request('TEST1', 'EXCH1', 0)
            gmock.assert_called_with(
                google.DUMMY_URLS[0].format('EXCH1%3ATEST1'))

            google.dummy_request('TEST4', 'EXCH4', 4)
            gmock.assert_called_with(
                google.DUMMY_URLS[0].format('EXCH4%3ATEST4'))

            google.dummy_request('TEST', '', 4)
            gmock.assert_called_with(
                google.DUMMY_URLS[0].format('TEST'))


class TestOptionChains(unittest.TestCase):

    def setUp(self):
        fake_http_service.install_data_file_http_handler()

    def test_request_option_chain_expirations(self):
        option_chain = google.request_options_chain('GOOG')
        expirations = option_chain.expirations
        self.assertEqual(12, len(expirations))
        self.assertListEqual([16, 8, 2014],
                             [expirations[0].day,
                              expirations[0].month,
                              expirations[0].year])
        self.assertEquals('20140816', str(expirations[0]))

        self.assertListEqual([15, 1, 2016],
                             [expirations[-1].day,
                              expirations[-1].month,
                              expirations[-1].year])
        self.assertEquals('20160115', str(expirations[-1]))

    def test_request_option_chain_calls(self):
        option_chain = google.request_options_chain('GOOG')
        calls = option_chain.calls
        self.assertEqual(151, len(calls))

        self.assertDictEqual({'a': '58.40', 'c': '-', 'b': '57.95',
                              'e': 'OPRA', 'name': '', 'oi': '0',
                              'cid': '985928489129434', 'vol': '-',
                              'expiry': 'Aug 16, 2014', 'p': '-',
                              's': 'AAPL140816C00037860', 'strike': '37.86'},
                             calls[0].data)

        self.assertDictEqual({'a': '0.01', 'c': '0.00', 'b': '-',
                              'e': 'OPRA', 'name': '', 'oi': '633',
                              'cid': '791404271676757', 'vol': '-',
                              'expiry': 'Aug 16, 2014', 'p': '0.01',
                              's': 'AAPL140816C00140000', 'cs': 'chb',
                              'cp': '0.00', 'strike': '140.00'},
                             calls[-1].data)

    def test_request_option_chain_puts(self):
        option_chain = google.request_options_chain('GOOG')
        puts = option_chain.puts
        self.assertEqual(151, len(puts))

        self.assertDictEqual({'a': '0.01', 'c': '-', 'b': '-',
                              'e': 'OPRA', 'name': '', 'oi': '700',
                              'cid': '597723653891363', 'vol': '-',
                              'expiry': 'Aug 16, 2014', 'p': '-',
                              's': 'AAPL140816P00037860', 'strike': '37.86'},
                             puts[0].data)

        self.assertDictEqual({'a': '44.25', 'c': '0.00', 'b': '43.75',
                              'e': 'OPRA', 'name': '', 'oi': '1455',
                              'cid': '247391588317856', 'vol': '-',
                              'expiry': 'Aug 16, 2014', 'p': '45.00',
                              's': 'AAPL140816P00140000', 'cs': 'chb',
                              'cp': '0.00', 'strike': '140.00'},
                             puts[-1].data)

    def test_to_list(self):
        option_chain = google.request_options_chain('GOOG')
        calls = option_chain.calls
        puts = option_chain.puts

        self.assertListEqual(['ASK', 'BID', 'CHANGE', 'OPEN_INTEREST',
                              'VOLUME', 'LAST_PRICE', 'STRIKE',
                              'PERCENT_CHANGE'],
                              [item for item in google.OptionChain.FIELDS])
        self.assertListEqual(['58.40', '57.95', '-', '0', '-', '-',
                              '37.86', ''],
                             calls[0].to_list())
        self.assertListEqual(['0.01', '-', '-', '700', '-', '-', '37.86', ''],
                             puts[0].to_list())

    def test_zero_pad(self):
        self.assertEqual('01', google.ExpiryDate._zero_pad(1))
        self.assertEqual('10', google.ExpiryDate._zero_pad(10))

    def test_empty_chain(self):
        # TODO: Find out why not working
        option_chain = google.request_options_chain('EMPTY')
        self.assertEqual(google.OptionChainResponse, type(option_chain))
        self.assertFalse(option_chain.is_valid)

    def test_call_only(self):
        option_chain = google.request_options_chain('CALL_ONLY')
        self.assertEqual(1, len(option_chain.calls))
        self.assertEqual(0, len(option_chain.puts))

    @patch.object(urllib2, 'urlopen')
    def test_http_400_response(self, mock_urlopen):
        error = urllib2.HTTPError(
            url='', code=400, msg='Bad Request', hdrs=None, fp=None)
        mock_urlopen.side_effect = error

        self.assertEquals(google.BadResponse,
                          type(google.request_options_chain('INVALID')))

    @patch.object(urllib2, 'urlopen')
    def test_http_503_response(self, mock_urlopen):
        error = urllib2.HTTPError(
            url='', code=503, msg='Service Unavailable', hdrs=None, fp=None)
        mock_urlopen.side_effect = error

        self.assertRaises(urllib2.HTTPError,
                          google.request_options_chain, 'INVALID')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestGoogle").setLevel(logging.DEBUG)
    test_classes_to_run = [TestGoogle, TestOptionChains]
    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
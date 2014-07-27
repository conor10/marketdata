import datetime as dt
import logging
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


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestGoogle").setLevel(logging.DEBUG)
    unittest.main()

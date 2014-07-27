from abc import abstractmethod
import datetime as dt
import pytz
import simplejson
import logging
import urllib
import urllib2


# Complete exchange list:
# http://www.google.com/intl/en/googlefinance/disclaimer/

"""Parameter is passed as <symbol>:<exchange> tuple."""
QUOTE_URL = 'http://finance.google.com/finance/info?'

"""Price url provides timeseries price data for instruments."""
PRICE_URL = 'http://www.google.com/finance/getprices?'


def request_quote(symbols, exchange='NASDAQ'):
    """Encode arguments in format sym1:EXCH&sym2:EXCH&..."""
    request_url = QUOTE_URL + 'q=' + \
                  '&'.join([exchange + ':' + symbol for symbol in symbols])

    response = _send_request(request_url)
    return QuoteResponse(response)


def _send_request(url):
    return urllib2.urlopen(url)


class Response(object):
    def __init__(self, content):
        self.data = self._parse_response(content)

    @property
    def is_valid(self):
        return len(self.data) > 0

    @abstractmethod
    def _parse_response(self, content):
        pass


class QuoteResponse(Response):
    SYMBOL = 't'
    EXCHANGE = 'e'
    LAST_PRICE = 'l'
    LAST_PRICE_FIX = 'l_fix'
    LAST_PRICE_WITH_CURRENCY = 'l_cur'
    _S = 's'
    LAST_TRADE_TIME = 'ltt'
    LAST_TRADE_DATE_TIMESTAMP = 'lt'
    LAST_TRADE_DATE_TIMESTAMP_ISO = 'lt_dts'
    CHANGE_FROM_CLOSE = 'c'
    CHANGE_FROM_CLOSE_FIX = 'c_fix'
    _CP = 'cp'
    _CP_FIX = 'cp_fix'
    _CCOL = 'ccol'
    PREVIOUS_CLOSE = 'pcls_fix'
    DIVIDEND = 'div'
    YIELD = 'yld'

    def __init__(self, content):
        super(QuoteResponse, self).__init__(content)
        self.log = logging.getLogger(__name__)
        self._last_trade_time = self._parse_last_trade_time()

    def _parse_response(self, response):
        content = response.read()
        return simplejson.loads(content[2:])[0]

    @property
    def last_price(self):
        return float(self.data[self.LAST_PRICE])

    @property
    def last_trade_price(self):
        # Doesn't appear to be available
        pass

    @property
    def last_trade_time(self):
        return self._last_trade_time

    def _parse_last_trade_time(self):
        return self._build_timestamp_utc(
            self.data[self.LAST_TRADE_DATE_TIMESTAMP],
            self.data[self.LAST_TRADE_DATE_TIMESTAMP_ISO])

    @staticmethod
    def _build_timestamp_utc(date_ts, timestamp_iso):
        tz = date_ts.rsplit(' ')[-1]
        if 'GMT' in tz:
            tz_name = 'Etc/' + tz
        elif 'EDT' in tz:
            tz_name = 'EST5EDT'
        elif 'EST' in tz:
            tz_name = 'EST'
        else:
            return None

        pytz_tz = pytz.timezone(tz_name)
        timestamp = dt.datetime.strptime(timestamp_iso, '%Y-%m-%dT%H:%M:%SZ')
        local_timestamp = pytz_tz.localize(timestamp)
        return local_timestamp.astimezone(pytz.utc)

    def __repr__(self):
        return str([self.__dict__[key] for key in self.__dict__])


def request_prices(symbol, exchange='NASDAQ', interval=1, period='1d',
                   fields='d,o,h,l,c,v'):
    """Request prices data.

    :param symbol:
    :param exchange:
    :param interval: Interval between points in seconds
    :param period:  Period of data, 1d = 1 day, 40Y = 40 years
    :param fields:  d = timestamp
                    o = open
                    c = close
                    h = high
                    l = low
                    v = volume
    :return: PriceResponse object containing underlying data
    """
    url = _encode_url(symbol, exchange, interval, period, fields)
    response = _send_request(url)
    return PriceResponse(response, interval)


def _encode_url(symbol, exchange, interval, period, fields):

    url_data = {'q': symbol, 'x': exchange, 'i': interval, 'p': period,
                'f': fields}
    url_values = urllib.urlencode(url_data)
    return PRICE_URL + url_values


class PriceResponse(Response):
    def __init__(self, response, interval):
        self.log = logging.getLogger(__name__)
        self.interval = interval
        self.current_timestamp = 0
        self.timestamp = []
        self.open_px = []
        self.high = []
        self.low = []
        self.close = []
        self.volume = []

        super(PriceResponse, self).__init__(response)

    def append(self, timestamp, open_px, high, low, close, volume):
        self.timestamp.append(timestamp)
        self.open_px.append(open_px)
        self.high.append(high)
        self.low.append(low)
        self.close.append(close)
        self.volume.append(volume)

    def _parse_response(self, response):
        csv_data = response.readlines()

        row_count = len(csv_data)
        if row_count < 8:
            self.log.error('Result set is too small, only {} rows returned'
                           .format(row_count))
            return

        result_interval = int(csv_data[3].split('=')[1])
        if result_interval != self.interval:
            self.log.error(
                'Interval returned ({}) does not match expected ({})'
                .format(result_interval, self.interval))
            return

        # Not used, but here for completeness
        timezone_offset = self._process_timezone_offset(csv_data[6])

        for i in xrange(7, row_count):
            entries = csv_data[i].count(',')
            if entries == 0 and csv_data[i].split('=')[0] == 'TIMEZONE_OFFSET':
                timezone_offset = self._process_timezone_offset(csv_data[i])
            elif entries == 6:
                self._process_csv_row(csv_data[i])
            else:
                print 'Unexpected result count {}'.format(entries)
                self.log.error('Unable to process row data: {}'
                               .format(entries, csv_data[i]))
                break

    @staticmethod
    def _process_timezone_offset(record):
        return record.split('=')[1]

    def _process_csv_row(self, data):
        offset, close, high, low, open_px, volume, cdays = \
            data.split(',')
        if offset[0] == 'a':
            self.current_timestamp = float(offset[1:])
            offset = 0
        else:
            offset = float(offset)
        open_px, high, low, close, volume = \
            [float(x) for x in [open_px, high, low, close, volume]]
        dt_timestamp = dt.datetime.utcfromtimestamp(
            self.current_timestamp + (self.interval * offset))
        self.append(dt_timestamp, open_px, high, low, close, volume)

    def to_csv(self):
        out = 'timestamp, open, high, low, close, volume\n'
        for i in range(0, len(self.timestamp)):
            out += '{0},{1},{2},{3},{4},{5}\n'.format(
                self.timestamp[i], self.open_px[i], self.high[i],
                self.low[i], self.close[i], self.volume[i])
        return out

    @property
    def length(self):
        return len(self.timestamp)

    def raw_data(self, index):
        return [self.timestamp[index], self.open_px[index], self.high[index],
                self.low[index], self.close[index], self.volume[index]]
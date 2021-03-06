from abc import abstractmethod
from abc import abstractproperty
from collections import OrderedDict
import datetime as dt
import logging
import pytz
import simplejson
import urllib
import urllib2
import yaml

from feedhandlers import utils

# Complete exchange list:
# http://www.google.com/intl/en/googlefinance/disclaimer/

"""Parameter is passed as <symbol>:<exchange> tuple."""
QUOTE_URL = 'http://finance.google.com/finance/info?'

"""Price url provides timeseries price data for instruments."""
PRICE_URL = 'http://www.google.com/finance/getprices?'

"""Options chains. If we don't specify a date, the nearest expiry is returned
"""
OPTIONS_CHAIN_URL = 'http://www.google.com/finance/option_chain?' \
                    'q={}&output=json'
OPTIONS_CHAIN_DATE_URL = 'http://www.google.com/finance/option_chain?' \
                         'q={0}&expd={1}&expm={2}&expy={3}&output=json'

"""A real url that we don't want to process the response from."""
DUMMY_STOCK = 'http://www.google.com/finance?' \
            'q={}&ei=RhLiU4DJO8jxkQX7i4GgBg'
DUMMY_NEWS = 'http://www.google.com/finance/company_news?' \
             'q={}&ei=OK_mU4CCKc_ZkgWDy4HYBg'
DUMMY_CHART = 'http://www.google.com/finance?' \
              'chdnp=1&chdd=1&chds=1&chdv=1&chvs=maximized' \
              '&chdeh=0&chfdeh=0&chdet=1407503880000' \
              '&chddm=2011164&chls=IntervalBasedLine' \
              '&q={}&ntsp=0&ei=4uDmU-DOBcS4kAWpyIC4AQ'
DUMMY_OPTION = 'http://www.google.com/finance/option_chain?q={}'
DUMMY_URLS = [DUMMY_STOCK, DUMMY_NEWS, DUMMY_CHART, DUMMY_OPTION]


# The number of requests sent this session
request_count = 0


def dummy_request(symbol, exchange='', index=0):

    dummy_url = DUMMY_URLS[index % len(DUMMY_URLS)]

    if exchange is '':
        request_url = dummy_url.format(symbol)
    else:
        request_url = dummy_url.format(exchange + '%3A' + symbol)
    _send_request(request_url)


def request_quote(symbols, exchange='NASDAQ'):
    """Encode arguments in format sym1:EXCH&sym2:EXCH&..."""
    request_url = QUOTE_URL + 'q=' + \
                  '&'.join([exchange + ':' + symbol for symbol in symbols])

    response = _send_request(request_url)
    if response is None:
        return BadResponse()
    else:
        return QuoteResponse(response)


def _send_request(url):
    global request_count
    if request_count != 0 and request_count % 1900 == 0:
        utils.long_sleep()
    else:
        utils.random_sleep(0.5)
    request_count += 1

    logging.debug(url)
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        logging.error('Bad response for request: [url={}, error={}'
                      .format(url, e))
        if e.code == 400:
            # In this case re-requesting with NYSE/NASDAQ may work
            response = None
        else:
            raise

    return response


class Response(object):
    def __init__(self):
        pass

    @abstractproperty
    def is_valid(self):
        pass

    @abstractmethod
    def _parse_response(self, content):
        pass


class BadResponse(Response):
    @property
    def is_valid(self):
        return False

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
    _CP = 'cp' # Percent change during trading
    _CP_FIX = 'cp_fix'
    _CCOL = 'ccol'
    PREVIOUS_CLOSE = 'pcls_fix'
    DIVIDEND = 'div'
    YIELD = 'yld'

    def __init__(self, content):
        super(QuoteResponse, self).__init__()
        self.data = self._parse_response(content)
        self.log = logging.getLogger(__name__)
        self._last_trade_time = self._parse_last_trade_time()

    @property
    def is_valid(self):
        return len(self.data) > 0

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


def request_prices(symbol, exchange='', interval=60, period='1d',
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
        super(PriceResponse, self).__init__()

        self.log = logging.getLogger(__name__)
        self.interval = interval
        self.current_timestamp = 0
        self.timestamp = []
        self.open_px = []
        self.high = []
        self.low = []
        self.close = []
        self.volume = []

        self._parse_response(response)

    def append(self, timestamp, open_px, high, low, close, volume):
        self.timestamp.append(timestamp)
        self.open_px.append(open_px)
        self.high.append(high)
        self.low.append(low)
        self.close.append(close)
        self.volume.append(volume)

    @property
    def is_valid(self):
        return len(self.timestamp) > 0

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
            elif entries == 5 or entries == 6:
                # The CDATA field may or may not be present
                self._process_csv_row(csv_data[i])
            else:
                self.log.error('Unable to process row data: {}'
                               .format(csv_data[i]))
                break

    @staticmethod
    def _process_timezone_offset(record):
        return record.split('=')[1]

    def _process_csv_row(self, data):
        record = data.split(',')

        offset = record[0]
        close = record[1]
        high = record[2]
        low = record[3]
        open_px = record[4]
        volume = record[5]

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
        out = 'timestamp,open,high,low,close,volume\n'
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


def request_options_chain(symbol, expiry_day=None,
                          expiry_month=None, expiry_year=None):

    url = _create_option_request_url(symbol, expiry_day, expiry_month,
                                     expiry_year)

    response = _send_request(url)
    if response is None:
        return BadResponse()
    else:
        return OptionChainResponse(response)


def _create_option_request_url(symbol, expiry_day, expiry_month, expiry_year):
    if expiry_day is None or expiry_month is None or expiry_year is None:
        return OPTIONS_CHAIN_URL.format(symbol)
    else:
        return OPTIONS_CHAIN_DATE_URL.format(symbol, expiry_day, expiry_month,
                                             expiry_year)


class OptionChainResponse(Response):
    def __init__(self, data):
        super(OptionChainResponse, self).__init__()
        self._data = None
        self._expirations = None
        self._expiry = None
        self._calls = None
        self._puts = None

        self.log = logging.getLogger(__name__)

        self._parse_response(data)

    @property
    def is_valid(self):
        # Contains fields expiry, expirations, underlying_id, underlying_price
        # No put or calls results in two fields only
        return len(self._data) > 3

    def _parse_response(self, response):
        data = response.read()
        """ As key values are not quoted in the response, it is not
        considered valid JSON. We can convert to a Yaml parser friendly
        format by simply adding a space after each colon key/value
        pair separator
        """
        self._data = yaml.load(data.replace(':', ': '))
        if not self.is_valid:
            return

        self._expiry = ExpiryDate(self._data['expiry'])
        self._expirations = [ExpiryDate(x) for x in self._data['expirations']]

    @property
    def expirations(self):
        return self._expirations

    @property
    def expiry(self):
        return self._expiry

    @property
    def calls(self):
        if self._calls is None:
            if 'calls' in self._data:
                self._calls = [OptionChain(x) for x in self._data['calls']]
            else:
                self._calls = []
        return self._calls

    @property
    def puts(self):
        if self._puts is None:
            if 'puts' in self._data:
                self._puts = [OptionChain(x) for x in self._data['puts']]
            else:
                self._puts = []
        return self._puts


class OptionChain(object):

    FIELDS = OrderedDict([
        ('ASK', 'a'),
        ('BID', 'b'),
        ('CHANGE', 'c'),
        ('OPEN_INTEREST', 'oi'),
        ('VOLUME', 'vol'),
        ('LAST_PRICE', 'p'),
        ('STRIKE', 'strike'),
        ('PERCENT_CHANGE', 'cp')
    ])


    def __init__(self, data):
        self._data = data

    @property
    def ask(self):
        return self._data['a']

    @property
    def bid(self):
        return self._data['b']

    @property
    def change(self):
        return self._data['c']

    @property
    def exchange(self):
        return self._data['e']

    @property
    def name(self):
        # Always '' at the time of writing
        return self._data['name']

    @property
    def open_interest(self):
        return self._data['oi']

    @property
    def contract_id(self):
        return self._data['cid']

    @property
    def volume(self):
        return self._data['vol']

    @property
    def expiry(self):
        return self._data['expiry']

    @property
    def last_price(self):
        return self._data['p']

    @property
    def symbol(self):
        return self._data['s']

    @property
    def strike(self):
        return self._data['strike']

    @property
    def cs(self):
        # TODO: Find out what this means
        # values 'chb', 'chr'
        return self._data['cs']

    @property
    def percent_change(self):
        return self._data['cp']

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return str(self._data)

    def to_list(self):
        results = []
        for field in OptionChain.FIELDS.values():
            if field in self._data:
                results.append(self._data[field])
            else:
                results.append('')
        return results



class ExpiryDate(object):
    def __init__(self, data):
        self._data = data

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @property
    def year(self):
        return self._data['y']

    @property
    def month(self):
        return self._data['m']

    @property
    def day(self):
        return self._data['d']

    def __repr__(self):
        return str(self.year) + self._zero_pad(self.month) \
            + self._zero_pad(self.day)

    @staticmethod
    def _zero_pad(value):
        if value < 10:
            return '0' + str(value)
        else:
            return str(value)
import httplib
import os
from StringIO import StringIO
import urllib2

from feedhandlers.google import PRICE_URL, QUOTE_URL, OPTIONS_CHAIN_URL
from feedhandlers.yahoo import YAHOO_URL


GOOGLE_DIR = os.path.join('test', 'data', 'google')
GOOGLE_PRICE_DIR = os.path.join(GOOGLE_DIR, 'prices')
GOOGLE_QUOTE_DIR = os.path.join(GOOGLE_DIR, 'quotes')
GOOGLE_OPTION_DIR = os.path.join(GOOGLE_DIR, 'options')
YAHOO_DATA_DIR = os.path.join('test', 'data', 'yahoo')


def install_file_http_handler():
    FileHttpHandler()


def install_data_file_http_handler():
    DataFileHttpHandler()


class FileHttpHandler(urllib2.HTTPHandler):

    def __init__(self):
        # HTTPHandler does not inherit from object, so we cannot use super()
        urllib2.HTTPHandler.__init__(self)
        opener = urllib2.build_opener(self)
        urllib2.install_opener(opener)

    def http_open(self, req):
        url = req.get_full_url()
        if url is not None:
            header = httplib.HTTPMessage(StringIO(""))
            header["Content-Type"] = "text/html"
            header["Content-Length"] = "1234"

            resp = urllib2.addinfourl(StringIO("test data\n"), header, url)
            resp.code = 200
            resp.msg = "OK"
            return resp
        else:
            raise urllib2.HTTPError(404, url, "Invalid url specified: %s"
                                    % (req.get_full_url()), url, None)


class DataFileHttpHandler(urllib2.HTTPHandler):

    def __init__(self):
        # HTTPHandler does not inherit from object, so we cannot use super()
        urllib2.HTTPHandler.__init__(self)
        opener = urllib2.build_opener(self)
        urllib2.install_opener(opener)

    def http_open(self, req):
        url = req.get_full_url()
        split_url = req.get_full_url().split('?', 1)
        base_url = split_url[0] + '?'
        file_name = self._extract_quote_name(split_url[1])

        if not self._is_valid_base_url(base_url):
            raise urllib2.HTTPError(404, base_url,
                                    'Invalid base url specified {}'
                                    .format(base_url), url, None)

        file_path = self._get_file_path(base_url, file_name)

        if os.path.isfile(file_path):

            header = httplib.HTTPMessage(StringIO(""))
            header["Content-Type"] = "text/html"
            header["Content-Length"] = str(os.path.getsize(file_path))

            resp = urllib2.addinfourl(open(file_path), header, url)
            resp.code = 200
            resp.msg = "OK"
            return resp

        else:
            raise urllib2.HTTPError(404, url, "Invalid url specified: %s"
                                    % (req.get_full_url()), url, None)

    def _extract_quote_name(self, params):
        first_param = params.split('&')[0]
        return first_param.split('=')[1]

    def _is_valid_base_url(self, base_url):
        return base_url == PRICE_URL \
            or base_url == QUOTE_URL \
            or base_url == YAHOO_URL \
            or base_url == OPTIONS_CHAIN_URL.split('?')[0] + '?'

    def _get_file_path(self, base_url, file_name):
        if base_url == PRICE_URL:
            return os.path.join(GOOGLE_PRICE_DIR, file_name + '.csv')
        elif base_url == QUOTE_URL:
            return os.path.join(GOOGLE_QUOTE_DIR, file_name + '.json')
        elif base_url == YAHOO_URL:
            return os.path.join(YAHOO_DATA_DIR, file_name + '.csv')
        elif base_url == OPTIONS_CHAIN_URL.split('?')[0] + '?':
            return os.path.join(GOOGLE_OPTION_DIR, file_name + '.json')
        else:
            return None


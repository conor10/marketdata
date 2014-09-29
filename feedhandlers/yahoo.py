import os
import sys
import time
import urllib2

from matplotlib import finance

import utils


STOCK_LIST = 'https://au.finance.yahoo.com/q/cp?s=%5EFTSE'

# Provide symbol
OPTIONS_CHAIN_URL = 'http://query.yahooapis.com/v1/public/yql?' \
                    'q=select%20%2A%20from%20yahoo.finance.options%20' \
                    'where%20symbol%3D%22{}%22' \
                    '&env=store://datatables.org/alltableswithkeys&format=xml'

# Provide symbol, YYYY, MM
OPTIONS_CHAIN_DATE_URL = 'http://query.yahooapis.com/v1/public/yql?' \
                         'q=select%20%2A%20from%20yahoo.finance.options%20' \
                         'where%20symbol%3D%22{0}%22%20' \
                         'AND%20expiration%3D%22{1}-{2}%22' \
                         '&env=store://datatables.org/alltableswithkeys' \
                         '&format=xml'

YAHOO_URL = 'http://download.finance.yahoo.com/d/quotes.csv?'


def main():
    if len(sys.argv) != 3:
        print('Usage {}: <symbol-file> <destination-dir>'.format(sys.argv[0]))
        exit(1)

    symbols = utils.load_symbol_list(sys.argv[1])
    base_dir = sys.argv[2]

    for symbol in symbols:
        dest_dir = os.path.join(base_dir, symbol + '.csv')
        try:
            finance.fetch_historical_yahoo(symbol, (2000, 1, 1), (2014, 9, 21),
                                           cachename=dest_dir)
        except urllib2.URLError:
            print('Download failed for symbol: {}'.format(symbol))
        time.sleep(30)


if __name__ == '__main__':
    main()
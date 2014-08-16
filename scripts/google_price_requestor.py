import logging
import math
import os.path
import random
import sys
import time

from feedhandlers import google
from feedhandlers import utils
import init_logger


def main():
    if len(sys.argv) < 3:
        print('Usage: {} <symbol-list-file> <destination-directory> <exchange>'
              .format(os.path.basename(sys.argv[0])))
        exit(1)

    symbol_list_file = sys.argv[1]
    dest_dir = sys.argv[2]

    if len(sys.argv) == 4:
        exchange = sys.argv[3]

    symbols = utils.load_symbol_list(symbol_list_file)
    _trim_trailing_period(symbols)
    request_intraday_prices(symbols, exchange, dest_dir)


def request_intraday_prices(symbols, exchange, dest_dir):

    for index, symbol in enumerate(symbols):
        dest_file = os.path.join(dest_dir, symbol + '.csv')
        price_response = google.request_prices(symbol, exchange)

        if price_response.is_valid:
            csv_data = price_response.to_csv()
            with open(dest_file, 'w') as f:
                f.write(csv_data)
        else:
            logging.error('Invalid response received [symbol={}, exch={}]'
                          .format(symbol, exchange))

        alternate_symbol = _select_alternative_symbol(index, symbols)
        google.dummy_request(alternate_symbol, exchange, index)
        utils.random_sleep()


def _select_alternative_symbol(index, symbols):
    return symbols[(index + 10) % len(symbols)]


def _trim_trailing_period(symbols):
    for i in range(0, len(symbols)):
        symbol = symbols[i]
        if symbol[-1] == '.':
            symbols[i] = symbol[0:-1]


if __name__ == '__main__':
    init_logger.setup()
    main()
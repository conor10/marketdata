import logging
import os.path
import sys

import feedhandlers.google as google
import init_logger


def main():
    if len(sys.argv) != 4:
        print('Usage: {} <exchange> <symbol-list-file> <destination-directory>'
              .format(os.path.basename(sys.argv[0])))
        exit(1)

    exchange = sys.argv[1]
    symbol_list_file = sys.argv[2]
    dest_dir = sys.argv[3]

    symbols = load_symbol_list(symbol_list_file)
    _trim_trailing_period(symbols)
    request_intraday_prices(symbols, exchange, dest_dir)


def request_intraday_prices(symbols, exchange, dest_dir):
    for symbol in symbols:
        dest_file = os.path.join(dest_dir, symbol + '.csv')
        price_response = google.request_prices(symbol, exchange)

        if price_response.is_valid:
            csv_data = price_response.to_csv()
            with open(dest_file, 'w') as f:
                f.write(csv_data)
        else:
            logging.error('Invalid response received [symbol={}, exch={}]'
                         .format(symbol, exchange))

        alternate_symbol = _select_alternative_symbol(symbol, symbols)
        google.dummy_request(alternate_symbol, exchange)


def _select_alternative_symbol(symbol, symbols):
    index = symbols.index(symbol)
    return symbols[(index + 10) % len(symbols)]


def load_symbol_list(filename):
    try:
        logging.debug('Loading symbol list from {}'.format(filename))
        with open(filename, 'r') as f:
            return f.read().splitlines()
    except IOError:
        logging.error('Unable to open file: {}'.format(filename))
        return []


def _trim_trailing_period(symbols):
    for i in range(0, len(symbols)):
        symbol = symbols[i]
        if symbol[-1] == '.':
            symbols[i] = symbol[0:-1]


if __name__ == '__main__':
    init_logger.setup()
    main()
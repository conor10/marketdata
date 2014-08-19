import logging
import os
import sys

from feedhandlers import utils
from feedhandlers import google
import init_logger


def main():
    if len(sys.argv) != 3:
        print('Usage: {} <symbol-list-file> <destination-directory>'
              .format(os.path.basename(sys.argv[0])))
        exit(1)

    symbol_list = sys.argv[1]
    dest_dir = sys.argv[2]

    symbols = utils.load_symbol_list(symbol_list)

    for symbol in symbols:
        _request_option_chains(symbol, dest_dir)


def _request_option_chains(symbol, dest_dir):
    option_chain = google.request_options_chain(symbol)

    if option_chain.is_valid:
        _write_chain(symbol, option_chain, dest_dir)
    else:
        logging.warn(
            'Invalid option chain received for symbol: {}'.format(symbol))
        return

    # exclude expiration we already have
    expirations = [exp for exp in option_chain.expirations
                   if exp is not option_chain.expiry]
    _request_expirations_chains(symbol, expirations, dest_dir)


def _request_expirations_chains(symbol, expirations, dest_dir):
    for expiry in expirations:

        # Perform dummy request first
        google.dummy_request(symbol)

        option_chain = google.request_options_chain(
            symbol,
            expiry_day=expiry.day,
            expiry_month=expiry.month,
            expiry_year=expiry.year)

        if option_chain.is_valid:
            _write_chain(symbol, option_chain, dest_dir)
        else:
            logging.warn('Invalid option chain received for symbol: {0}, '
                         'expiry: y={1}, m={2}, d={3} '
                         .format(symbol, expiry.year,
                                 expiry.month, expiry.day))


def _write_chain(symbol, option_chain, dest_dir):
    expiry = option_chain.expiry
    dest_calls_file = os.path.join(dest_dir,
                                   symbol + str(expiry) + 'C' + '.csv')
    dest_puts_file = os.path.join(dest_dir,
                                  symbol + str(expiry) + 'P' + '.csv')

    _write_file(dest_calls_file, option_chain.calls)
    _write_file(dest_puts_file, option_chain.puts)


def _write_file(file_name, data):
    with open(file_name, 'w') as f:
        f.write(','.join(google.OptionChain.FIELDS) + '\n')
        for item in data:
            f.write(','.join(item.to_list()) + '\n')


if __name__ == '__main__':
    init_logger.setup()
    main()
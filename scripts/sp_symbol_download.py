import logging
import os
import sys
import urllib2

import init_logger
import feedhandlers.standardandpoors as sp


URL_MAP = {'SP500': sp.SP500_URL, 'ASX200': sp.ASX200_URL}

DEST_FILE = 'symbols.txt'


def main():
    if len(sys.argv) != 3:
        _exit_with_usage()

    index = sys.argv[1]
    dest_dir = sys.argv[2]

    if index not in URL_MAP:
        _exit_with_usage()

    url = URL_MAP[index]
    destination = os.path.join(dest_dir, DEST_FILE)

    logging.debug(url)
    response = urllib2.urlopen(url)
    symbols = sp.parse_response(response)

    _write_symbols(symbols, destination)


def _exit_with_usage():
    print('Usage: {} [SP500|ASX200] <destination-directory>'
          .format(os.path.basename(sys.argv[0])))
    exit(1)


def _write_symbols(symbols, destination):
    with open(destination, 'w') as f:
        for symbol in symbols:
            f.write(symbol + '\n')


if __name__ == '__main__':
    init_logger.setup()
    main()
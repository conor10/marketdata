import logging
import math
import random
import time


random.seed(10)


LONG_SLEEP_DURATION = 60 * 15


def load_symbol_list(filename):
    try:
        logging.debug('Loading symbol list from {}'.format(filename))
        with open(filename, 'r') as f:
            symbol_list = f.read().splitlines()
            if len(symbol_list) > 0:
                return symbol_list
            else:
                raise InvalidFileException(
                    'symbol list file: {} is empty'.format(filename))
    except IOError:
        raise InvalidFileException('Unable to open file: {}'.format(filename))


def random_sleep(interval=0.5):
    interval = math.fabs(random.random() - interval)
    time.sleep(interval)


def long_sleep(interval=LONG_SLEEP_DURATION):
    logging.debug('Entering {} second sleep...'.format(interval))
    time.sleep(interval)
    logging.debug('Woken up')


class InvalidFileException(Exception):
    pass

import csv
import glob
import os
import shutil
import sys

import pandas as pd


def main(dates=[]):
    basedir = os.path.join(sys.argv[1])
    if len(dates) == 0:
        dates = os.listdir(basedir)
        dates.sort()

    data = {}

    for date in dates:

        prices_dir = os.path.join(basedir, date, '*[0-9]*[PC].csv')
        files = glob.glob(prices_dir)

        for file in files:
            print('running on file {}'.format(file))
            process_file(file)
            verify(file + '.new')
            shutil.move(file + '.new', file)


def process_file(filename):
    with open(filename, 'r') as source_file, \
            open(filename + '.new', 'w') as dest_file:
        reader = csv.reader(source_file)
        for idx, row in enumerate(reader):
            if idx == 0:
                dest_file.write(','.join(row) + '\n')
                continue
            elif len(row) == 8:
                pass
            elif len(row) == 9:
                if check_idx(row, 0):
                    join_items(row, 0, 1)
                elif check_idx(row, 1):
                    join_items(row, 1, 2)
                elif check_idx(row, 5):
                    join_items(row, 5, 6)
                elif check_idx(row, 6):
                    join_items(row, 6, 7)
                elif check_idx(row, 7):
                    join_items(row, 7, 8)
            elif len(row) == 10:
                if check_idx(row, 0):
                    join_items(row, 0, 1)
                if check_idx(row, 1):
                    join_items(row, 1, 2)
                if check_idx(row, 5):
                    join_items(row, 5, 6)
                if check_idx(row, 6):
                    join_items(row, 6, 7)
                if check_idx(row, 7):
                    join_items(row, 7, 8)
            else:
                raise ProcessingException(
                    'Bad length row, {} elements'.format(len(row)))

            dest_file.write('"' + '","'.join(row) + '"\n')


def check_idx(list, idx):
    return (len(list[idx]) == 1 or len(list[idx]) == 2) and list[idx].isdigit()


def join_items(list, idx1, idx2):
    list[idx1:idx2 + 1] = [''.join(list[idx1] + ',' + list[idx2])]


def verify(filename):
    df = pd.read_csv(filename, index_col='STRIKE', thousands=',')
    print('file: {} loaded successfully'.format(filename))


class ProcessingException(Exception):
    pass


if __name__ == "__main__":
    main()

from os import path
import sys
import urllib2


BASE_URL = 'http://cfe.cboe.com/Publish/ScheduledTask/MktData/datahouse/'

MONTHS = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
YEARS = range(4, 16)


def main():
    if len(sys.argv) != 2:
        print('Destination directory not specified')
        sys.exit(1)

    dest_dir = sys.argv[1]

    for year in YEARS:
        for month in MONTHS:
            filename = 'CFE_{}{:0>2}_VX.csv'.format(month, year)
            url = '{}{}'.format(BASE_URL, filename)

            destination = path.join(dest_dir, filename)
            if path.isfile(destination) and path.getsize(destination) > 0:
                print('{} already exists'.format(filename))
                continue

            try:
                response = urllib2.urlopen(url)
                with open(destination, 'wb') as f:
                    f.write(response.read())
            except urllib2.HTTPError as e:
                print('Error downloading: {}, error: {}'.format(url, e))


if __name__ == '__main__':
    main()
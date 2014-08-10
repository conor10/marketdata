from distutils.core import setup

setup(
    name='marketdata',
    description='Tick and symbol data download tools',
    author='Conor',
    author_email='conor10@gmail.com',
    version='0.1',
    packages=['feedhandlers'],
    data_files=[('config', ['config/logging.yaml',
                            'config/crontab.txt'])],
    scripts=['scripts/.profile',
             'scripts/common.sh',
             'scripts/ftse100_epic_download.sh',
             'scripts/ftse100_prices_download.sh',
             'scripts/ftse100_symbol_download.sh',
             'scripts/google_price_requestor.py',
             'scripts/init_logger.py',
             'scripts/push_symbol_updates_s3.sh',
             'scripts/push_price_updates_s3.sh',
             'scripts/runner',
             'scripts/sp_symbol_download.py',
             'scripts/yahoo_urls.txt',
             'scripts/sp500_prices_download.sh',
             'scripts/sp500_symbol_download.sh',
             'scripts/asx200_prices_download.sh',
             'scripts/asx200_symbol_download.sh',
             'scripts/roll_symbols.sh']
)
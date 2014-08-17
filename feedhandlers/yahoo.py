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
# Common environment variables and configuration

export BASE_DIR="${HOME}/trading"

export SYMBOL_DIR="${BASE_DIR}/symbols"
export PRICE_DIR="${BASE_DIR}/prices"
export CHAIN_DIR="${BASE_DIR}/chains"

export PYTHONPATH="${BASE_DIR}/marketdata:${PYTHONPATH}"
export LOG_CFG="${BASE_DIR}/marketdata/config/logging.yaml"

export FTSE100_SYMBOLS="${SYMBOL_DIR}/FTSE100"
export FTSE100_PRICES="${PRICE_DIR}/FTSE100"

export SP500_SYMBOLS="${SYMBOL_DIR}/SP500"
export SP500_PRICES="${PRICE_DIR}/SP500"
export SP500_CHAINS="${CHAIN_DIR}/SP500"

export ASX200_SYMBOLS="${SYMBOL_DIR}/ASX200"
export ASX200_PRICES="${PRICE_DIR}/ASX200"

export VIX_SYMBOLS="${SYMBOL_DIR}/VIX"
export VIX_PRICES="${PRICE_DIR}/VIX"

export EMAIL_RECIPIENTS="conor10@gmail.com"
export SMS_RECIPIENTS="+61448593948"

# Common environment variables and configuration

export BASE_DIR="${HOME}/trading"

export SYMBOL_DIR="${BASE_DIR}/symbols"
export PRICE_DIR="${BASE_DIR}/prices"

export PYTHONPATH="${BASE_DIR}/marketdata:${PYTHONPATH}"
export LOG_CFG="${BASE_DIR}/marketdata/config/logging.yaml"

export FTSE100_SYMBOLS="${SYMBOL_DIR}/FTSE100"
export FTSE100_PRICES="${PRICE_DIR}/FTSE100"


#!/bin/bash

DEST_DIR="${FTSE100_PRICES}/${DATE}"
SYMBOL_LIST="${FTSE100_SYMBOLS}/current/symbols.txt"
REQUESTOR="$(dirname $0)/google_price_requestor.py"
EXCHANGE="LON"

main() {
  create_dir "${DEST_DIR}"
  /usr/bin/env python "$REQUESTOR" "${SYMBOL_LIST}" "${DEST_DIR}" "${EXCHANGE}"
}


main "$@"
